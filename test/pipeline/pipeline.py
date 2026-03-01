import sys

import pandas as pd


print("arguments", sys.argv)

month = int(sys.argv[1])


df = pd.DataFrame({"day": [1, 2], "number_passengers": [300, 400]})
df['month'] = month
print(df.head())

# a file format that is optimized for reading and writing tabular data, and is often used in data processing pipelines.
# It is a columnar storage file format that allows for efficient compression and encoding of data, making it faster to read and write compared to other formats like CSV or JSON.
df.to_parquet(f"output_day_{sys.argv[1]}.parquet")



print(f"Running pipeline for month={month}")
