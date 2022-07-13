import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
reddit_gaming_df = pd.read_csv('Top 100 posts in a subreddit.csv', sep='|', parse_dates=['Date'])[:100]
print(reddit_gaming_df)


