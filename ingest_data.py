#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
from tqdm.auto import tqdm
from sqlalchemy import create_engine
# just to see the progress

dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}


parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]


def run():

    year = 2021
    month = 1
    pg_user = 'root'
    pg_password = 'root'
    pg_host = 'localhost'
    pg_port = '5432'
    pg_db = 'ny_taxi'
    chunck_size = 100000

# prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
# df = pd.read_csv(prefix + 'yellow_tripdata_2021-01.csv.gz', nrows=100)

    target_table = "yellow_taxi_data"
    prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
    url = f'{prefix}/yellow_tripdata_{year}-{month:02d}.csv.gz'


    eng_url = f'postgresql+psycopg://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}'

    engine = create_engine('postgresql+psycopg://root:root@localhost:5432/ny_taxi')


    df_iter = pd.read_csv(
    url,
    dtype=dtype,
    parse_dates=parse_dates,
    iterator=True,
    chunksize=chunck_size)

    first = True

    for df_chunk in tqdm(df_iter):

        if first:
            # Create table schema (no data)
            df_chunk.head(0).to_sql(
                name=target_table,
                con=engine,
                if_exists="replace"
            )
            first = False
            print("Table created")

        # Insert chunk
        df_chunk.to_sql(
            name=target_table,
            con=engine,
            if_exists="append"
        )

        print("Inserted:", len(df_chunk))


if __name__ == '__main__':
    run()
