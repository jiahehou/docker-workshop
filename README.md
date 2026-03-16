# docker-workshop
Workshop codespaces

common image:
1. `docker run -it ubuntu` enter into the virtual env space you created and things can be isolated inside that env space
    - every time you run it, you will enter into a brand new env (env is something like duplicate based on the Docker Image)

2. install python in that env space
3. control+c, exit to go back to host machine


different image:
1. `docker run -it python:3.13.11-slim` Docker Image is a smaller package of python:3.13.11
    - This one starts python. If we want bash, we need to overwrite entrypoint
2. bash entry: `docker run -it --entrypoint=bash python:3.13.11-slim`


show enviroments we created based off of image:
1. `docker ps -a`
2. say if we need to clean all the envs: ``` docker rm `docker ps -aq` ```


set initial state in a reproducible manner --- volumes
`docker run -it -v $(pwd)/test:/app/test --entrypoint=bash python:3.9.16-slim`
- `$(pwd)/test` folder in host machine
- `/app/test` target location in docker


manage VM --- uv
fast Python package and project manager written in Rust. It's much faster than pip and handles virtual environments automatically.
`uv init --python=3.13`
 - This creates a pyproject.toml file for managing dependencies and a .python-version file.
 `uv run which python`  # Python in the virtual environment
 `uv add pandas pyarrow` This adds pandas to your pyproject.toml and installs it in the virtual environment.
 `uv run` to run everything!

---
## Dockerizing
1. write Dockerfile
2. build docker: `docker build -t test:pandas .`

    directory: place you save Dockerfile
    `test`: image
    `pandas`: given name of you wish

3. run docker: `docker run -it --entrypoint=bash --rm  test:pandas`
    `--rm` means you want to remove this state save when closing docker container

---
## Small summary
1. cd into the folder containing Dockerfile
2. run `docker build -t test:pandas .` to build docker
3. run `docker run -it --entrypoint=bash --rm test:pandas` run docker

1. way to get the project level env: `source /workspaces/docker-workshop/.venv/bin/activate`


---
## Running PostgreSQL in a Container

How to run container:
```
docker run -it --rm \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v ny_taxi_postgres_data:/var/lib/postgresql \
  -p 5432:5432 \
  postgres:18
```

### Explanation of Parameters

* `-e` sets environment variables (user, password, database name)
* `-v ny_taxi_postgres_data:/var/lib/postgresql` creates a **named volume**
  * Docker manages this volume automatically
  * Data persists even after container is removed
  * Volume is stored in Docker's internal storage
* `-p 5432:5432` maps port 5432 from container to host
* `postgres:18` uses PostgreSQL version 18 (latest as of Dec 2025)

### Alternative Approach - Bind Mount



First create the directory, then map it:

```
mkdir ny_taxi_postgres_data

docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql \
  -p 5432:5432 \
  postgres:18
```

## Connecting to PGCLI
1. `uv add --dev pgcli` always can only be run in the same folder with `pyproject.toml`

    in toml, the additional env can only be triggered by direct calling its name "dev"

        ```
        [dependency-groups]
        dev = [
            "pgcli>=4.4.0",
        ]

        ```

2. `uv run pgcli -h localhost -p 5432 -u root -d ny_taxi`

* `uv run` executes a command in the context of the virtual environment
* `-h` is the host. Since we're running locally we can use `localhost`.
* `-p` is the port.
* `-u` is the username.
* `-d` is the database name.
* The password is not provided; it will be requested after running the command.

When prompted, enter the password: `root`

3. exit just control c
4. want to run/reconnect to DB again? just run step 2 again.

## Basic SQL Commands

Try some SQL commands:

```sql
-- List tables
\dt

-- Create a test table
CREATE TABLE test (id INTEGER, name VARCHAR(50));

-- Insert data
INSERT INTO test VALUES (1, 'Hello Docker');

-- Query data
SELECT * FROM test;

-- Exit
\q
```

## NY Taxi Dataset and Data Ingestion - using jupyter
1. install jupyter: `uv add --dev jupyter`
2. run it: `uv run jupyter notebook`

### Install SQLAlchemy to ingest Data into Postgres
1. `uv add sqlalchemy "psycopg[binary,pool]"`
2. Create Database Connection
    ```
    from sqlalchemy import create_engine
    engine = create_engine('postgresql+psycopg://root:root@localhost:5432/ny_taxi')
    ```
3. Get DDL Schema: `print(pd.io.sql.get_schema(df, name='yellow_taxi_data', con=engine))`
4. create table: `df.head(n=0).to_sql(name='yellow_taxi_data', con=engine, if_exists='replace')`
5. Ingesting Data in Chunks: We don't want to insert all the data at once. Let's do it in batches and use an iterator for that:
    ```python
    df_iter = pd.read_csv(
        prefix + 'yellow_tripdata_2021-01.csv.gz',
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=100000
    )
    ```
6. inserting: `df_chunk.to_sql(name='yellow_taxi_data', con=engine, if_exists='append')`

## `uv run jupyter nbconvert --to=script <JUPYTER_FILE>` --> to save to .py
