"""

Utility script to archive files.

Usage:
> python3 archiver <HISTORY FILENAME> <N> <SYMBOL> <DATE 1> <DATE 2> ... <DATE N>

To read archived file using pandas:-
>>> import pandas as pd
>>> pd.read_csv("data/archive/<FILENAME>.csv.gz")
"""

import pandas as pd
import sys


def main():
    filename = sys.argv[1]
    n = int(sys.argv[2])
    symbol = sys.argv[3]
    dates = []
    for i in range(n):
        dates.append(sys.argv[i + 4])

    df = pd.read_csv(f"data/history/{filename}.csv")
    df['created_at'] = pd.to_datetime(df['created_at'])
    for date in dates:
        tbl = df[(df['created_at'] >= date) & (df['created_at'] < str(int(date) + 1))]
        tbl.to_csv(f"data/archive/{symbol}_{date}.csv.gz", compression='gzip', index=False)


main()
