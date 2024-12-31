import pandas as pd

def profit_factor(df_trades):
    profit_sum = df_trades.loc[df_trades['closed'] >= 0, 'closed'].sum()
    loss_sum = df_trades.loc[df_trades['closed'] < 0, 'closed'].sum()
    return profit_sum / abs(loss_sum)

data = {
    'id': [1, 2, 3, 4, 5, 6, 7],
    'closed': [130, -50, -50, 150, 100, -33, 115]
}

df = pd.DataFrame(data, columns=['id', 'closed'])
print(profit_factor(df))
