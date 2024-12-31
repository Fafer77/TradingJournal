import pandas as pd
import numpy as np

def sortino_ratio(df):
    estimated_return = df['result'].mean()
    downside_deviation = np.sqrt(np.mean(df.loc[df['result'] < 0, 'result'] ** 2))
    if downside_deviation == 0:
        return float('inf') if estimated_return > 0 else 0

    return estimated_return / downside_deviation

# test data
test_data = {
    'trade_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
                 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'result': [0.03, -0.005, 0.03, -0.005, 0.03,
               0.03, -0.005, 0.03, -0.005, 0.03,
               0.025, -0.005, -0.005, 0.02, 0.03,
               0.025, 0.025, -0.005, -0.005, 0.03,
               0.02, 0.025, -0.005, 0.025, -0.005]
}

df = pd.DataFrame(test_data)
print(sortino_ratio(df))

