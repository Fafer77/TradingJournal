import numpy as np
import pandas as pd
"""
Data:
R[i] - profit/loss in %
SR = E[Rp]/sda(R)
"""
def sharpe_ratio(df_trades):
    estimated_return = df_trades['result'].mean()
    sda = np.std(df_trades['result'], ddof=1)
    return estimated_return / sda

# test data
test_data = {
    'trade_id': [1, 2, 3, 4, 5],
    'result': [0.03, -0.01, 0.03, -0.005, 0.03]
}

df = pd.DataFrame(test_data)
print(sharpe_ratio(df))
