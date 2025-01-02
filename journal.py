import pandas as pd
from datetime import datetime
import sqlite3
import matplotlib.pyplot as plt


class Journal:
    def __init__(self):
        self.conn = sqlite3.connect('trades.db')
        self.cursor = self.conn.cursor()

        self._init_db()

        stats = self._fetch_stats()

        if stats:
            self.wins = stats[1]
            self.losses = stats[2]
            self.current_balance = stats[3]
            self.trade_with_plan = stats[4]
            self.trade_against_plan = stats[5]
            self.max_drawdown = stats[6]
        else:
            self.initialize_balance()
        
        self._columns = ['instrument', 'direction', 'position_size',
                         'entry_price', 'exit_price', 'entry_date',
                         'exit_date', 'commission', 'profit', 'with_plan']
        self.trades = self._load_trades()


    def add_trade(self):
        while True:  
            try:
                instrument = input("Instrument: ")
                direction = input("Direction (long/short): ")
                position_size = float(input("Position size (lots): "))
                entry_price = float(input("Entry price: "))
                exit_price = float(input("Exit price: "))
                entry_date = datetime.strptime(input("Entry date (YYYY-MM-DD HH:MM:SS): "), "%Y-%m-%d %H:%M:%S")
                exit_date = datetime.strptime(input("Exit date (YYYY-MM-DD HH:MM:SS): "), "%Y-%m-%d %H:%M:%S")
                commission = float(input("Commission: "))
                profit = float(input("Profit: "))
                plan = input("Was this trade in line with plan (yes/no): ").lower()

                entry_date_str = entry_date.strftime("%Y-%m-%d %H:%M:%S")
                exit_date_str = exit_date.strftime("%Y-%m-%d %H:%M:%S")
                
                break
            except ValueError:
                print("Invalid input. Please try again using the correct formats.\n-----------------------------------------------------")
        
        new_row = pd.DataFrame([{
            'instrument': instrument,
            'direction': direction,
            'position_size': position_size,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'entry_date': entry_date_str,
            'exit_date': exit_date_str,
            'commission': commission,
            'profit': profit,
            'with_plan': plan
        }], columns=self._columns)

        new_row.to_sql('trades', self.conn, if_exists='append', index=False)

        self.trades = pd.concat([self.trades.dropna(how="all", axis=1),
                                  new_row.dropna(how="all", axis=1)], 
                                  ignore_index=True)


        new_balance = self.current_balance + profit
        self._record_statistics_history(new_balance)


    def get_trade_history(self):
        return self.trades


    def statistics(self):
        self.plot_statistics()


    def plot_statistics(self):
        balance_history = self.get_statistics_history()

        if balance_history.empty:
            print('No balance history to plot')
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

        ax1.plot(balance_history['timestamp'], balance_history['balance'], marker='o', linestyle='-')
        ax1.legend()
        ax1.set_title('Balance History')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Balance')

        print(self.trade_against_plan, self.trade_with_plan)
        ax2.bar(['with plan', 'against plan'], [self.trade_with_plan, self.trade_against_plan])
        
        plt.tight_layout()
        plt.show()


    def _init_db(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                current_balance REAL DEFAULT 0,
                trade_with_plan INTEGER DEFAULT 0,
                trade_against_plan INTEGER DEFAULT 0,
                max_drawdown REAL DEFAULT 0
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instrument TEXT,
                direction TEXT,
                position_size REAL,
                entry_price REAL,
                exit_price REAL,
                entry_date TEXT,
                exit_date TEXT,
                commission REAL,
                profit REAL,
                with_plan TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE,
                balance REAL,
                trade_with_plan INTEGER,
                trade_against_plan INTEGER,
                profit REAL
                commission REAL
            )
        """)

        self.conn.commit()


    def _fetch_stats(self):
        self.cursor.execute("SELECT * FROM stats")
        row = self.cursor.fetchone()
        if row:
            return row
        return None


    def _save_default_stats(self, balance):
        self.cursor.execute("INSERT INTO stats (wins, losses, current_balance, trade_with_plan, trade_against_plan, max_drawdown) VALUES (?, ?, ?, ?, ?, ?)",
                            (0, 0, balance, 0, 0, 0))
        self.conn.commit()


    def update_stats(self, wins=None, losses=None, current_balance=None, 
                     trade_with_plan=None, trade_against_plan=None, 
                     max_drawdown=None):
        self.cursor.execute("""
            UPDATE stats SET
                wins = COALESCE(?, wins),
                losses = COALESCE(?, losses),
                current_balance = COALESCE(?, current_balance),
                trade_with_plan = COALESCE(?, trade_with_plan),
                trade_against_plan = COALESCE(?, trade_against_plan),
                max_drawdown = COALESCE(?, max_drawdown)
        """, (wins, losses, current_balance, trade_with_plan, trade_against_plan, max_drawdown))
        self.conn.commit()


    def is_db_empty(self):
        self.cursor.execute("SELECT COUNT(*) FROM stats")
        count = self.cursor.fetchone()[0]
        return count == 0
    

    def initialize_balance(self):
        while True:
            try:
                initial_balance = float(input("Enter initial balance: "))
                if initial_balance <= 0:
                    raise ValueError('Balance should be positive')
                break
            except ValueError as e:
                print(f"Invalid input. {e}. Please try again.\n----------------------------------------")

        self._save_default_stats(initial_balance)
        self.current_balance = initial_balance
        self._record_statistics_history(initial_balance)


    def _load_trades(self):
        query = """SELECT instrument, direction, position_size, entry_price, 
        exit_price, entry_date, exit_date, commission, profit, with_plan FROM 
        trades"""
        try:
            trades = pd.read_sql_query(query, self.conn)
            return trades
        except pd.io.sql.DatabaseError:
            return pd.DataFrame(columns=self._columns)


    def _record_statistics_history(self, balance):
        self.cursor.execute("""
            INSERT INTO statistics (balance) VALUES (?)
        """, (balance,))
        self.conn.commit()


    def get_statistics_history(self):
        query = """
            SELECT timestamp, balance FROM statistics ORDER BY timestamp ASC
        """
        try:
            statistics_history = pd.read_sql_query(query, self.conn, parse_dates=['timestamp'])
            return statistics_history
        except pd.io.sql.DatabaseError:
            return pd.DataFrame(columns=['timestamp', 'balance'])


    # it is used to aggregate statistics to daily period
    def update_daily_statistics(self, trade_date, profit, commission, 
                                with_plan):
        self.cursor.execute("SELECT * FROM statistics WHERE date = ?", (trade_date,))
        row = self.cursor.fetchone()

        trade_date = datetime.strptime(trade_date, "%Y-%m-%d").strftime("%Y-%m-%d")
        trade_with_plan = 1 if with_plan == 'yes' else 0
        trade_against_plan = 1 if with_plan == 'no' else 0

        if row:
            new_balance = row[2] + profit - commission
            new_profit = row[5] + profit
            new_trade_with_plan = row[3] + trade_with_plan
            new_trade_against_plan = row[4] + trade_against_plan
            new_commission = row[6] + commission
            self.cursor.execute("""
                UPDATE statistics SET balance = ?, trade_with_plan = ?, trade_against_plan = ?, profit = ?, commission = ?
                WHERE date = ?
            """, (new_balance, new_trade_with_plan, new_trade_against_plan, new_profit, new_commission, trade_date))
        else:
            previous_balance = self._get_previous_balance(trade_date)
            new_balance = previous_balance + profit - commission
            self.cursor.execute("""
                INSERT INTO statistics (date, balance, trade_with_plan,
                trade_against_plan, profit, commission)
                VALUES (?, ?, ?, ? ,?, ?)
                """, (trade_date, new_balance, trade_with_plan, 
                trade_against_plan, profit, commission))

        self.conn.commit()


    # helper function to get previous day balance
    def _get_previous_balance(self, trade_date):
        self.cursor.execute("""SELECT balance FROM statistics 
        WHERE date < ? ORDER BY date DESC LIMIT 1
        """, (trade_date,))
        row = self.cursor.fetchone()
        return row[0] if row else 0


    def __del__(self):
        try:
            self.cursor.close()
        finally:
            self.conn.close()
        
