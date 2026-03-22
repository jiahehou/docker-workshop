#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
from tqdm.auto import tqdm # just to see the progress
from sqlalchemy import create_engine

import click

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

@click.command()
@click.option('--year', default=2021, show_default=True, type=int, help='Data year')
@click.option('--month', default=1, show_default=True, type=int, help='Data month')
@click.option('--pg_user', default='root', show_default=True, help='PostgreSQL user')
@click.option('--pg_password', default='root', show_default=True, help='PostgreSQL password')
@click.option('--pg_host', default='localhost', show_default=True, help='PostgreSQL host')
@click.option('--pg_port', default='5432', show_default=True, help='PostgreSQL port')
@click.option('--pg_db', default='ny_taxi', show_default=True, help='PostgreSQL database name')
@click.option('--target_table', default='yellow_taxi_data', show_default=True, help='Target table name')
@click.option('--chunck_size', default=100000, show_default=True, type=int, help='CSV chunk size')
def run(year, month, pg_user, pg_password, pg_host, pg_port, pg_db, target_table, chunck_size):

# prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
# df = pd.read_csv(prefix + 'yellow_tripdata_2021-01.csv.gz', nrows=100)


    prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
    url = f'{prefix}/yellow_tripdata_{year}-{month:02d}.csv.gz'


    eng_url = f'postgresql+psycopg://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}'

    engine = create_engine(eng_url)


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
