import pandas as pd

def calc_win_rate(df):
    num_of_wins = df.loc[df['result'] >= 0, 'result'].sum()
    num_of_losses = df.loc[df['result'] < 0, 'result'].sum()
    return num_of_wins / num_of_losses
