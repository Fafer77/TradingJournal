import typer
from rich.console import Console
from journal import Journal
from rich.table import Table

app = typer.Typer()
console = Console()

journal = Journal()

@app.command()
def add_trade():
    journal.add_trade()
    console.print("[bold green]Trade added successfully![/bold green]")


@app.command()
def help():
    console.print("[bold cyan]Available commands: 'add-trade', 'run', 'exit'[/bold cyan]")


@app.command()
def show_statistics():
    pass


@app.command()
def print_balance_chart():
    journal.plot_statistics()


@app.command()
def trade_history():
    trades = journal.trade_history()
    if trades.empty:
        console.print("[bold red]No trades found.[/bold red]")
        return
    
    table = Table(title="Trade History", show_lines=True)

    for col in trades.columns:
        table.add_column(col, style='cyan', justify='center')
    
    for _, row in trades.iterrows():
        table.add_row(*[str(value) for value in list(row.values)])
    
    console.print(table)


@app.command()
def run():
    console.print("[bold magenta]Welcome to CLI app[/bold magenta]")
    console.print("""[bold cyan]Available commands: 'add-trade', 'trade-history' 'balance-chart', 'help', 'exit'[/bold cyan]""")

    while True:
        try:
            command = console.input("[bold green]> Enter command:[/bold green] ").strip().lower()

            if command == "add-trade":
                add_trade()
            elif command == "trade-history":
                trade_history()
            elif command == "balance-chart":
                print_balance_chart()
            elif command == "help":
                help()
            elif command in ("exit", "quit"):
                console.print("[bold yellow]Closing application...[/bold yellow]")
                break
            else:
                console.print("[bold red]Invalid command. Type 'help' for available commands.[/bold red]")
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Closing application...[/bold yellow]")
            break

if __name__ == "__main__":
    app()
