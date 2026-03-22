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
2. quick way to run this py

```
uv run python ingest_data.py \
  --pg_user=root \
  --pg_password=root \
  --pg_host=localhost \
  --pg_port=5432 \
  --pg_db=ny_taxi \
  --target_table=yellow_taxi_trips
```

## Docker Networks --> to make sure 2 separate contains can now be in the same network

1. `docker network create pg-network`

2. Build the Docker Image

```
cd pipeline
docker build -t taxi_ingest:v001 .
```

3. Run containerized ingestion

```
docker run -it --rm\
  --network=pg-network \
  taxi_ingest:v001 \
    --pg_user=root \
    --pg_password=root \
    --pg_host=pgdatabase \
    --pg_port=5432 \
    --pg_db=ny_taxi \
    --target_table=yellow_taxi_trips
```

### Run Containers on the Same Network

Stop both containers and re-run them with the network configuration:

```bash
# Run PostgreSQL on the network
docker run -it --rm\
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v ny_taxi_postgres_data:/var/lib/postgresql \
  -p 5432:5432 \
  --network=pg-network \
  --name pgdatabase \
  postgres:18

# In another terminal, run pgAdmin on the same network
docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -v pgadmin_data:/var/lib/pgadmin \
  -p 8085:80 \
  --network=pg-network \
  --name pgadmin \
  dpage/pgadmin4
```

PostgreSQL 是数据库服务器（Postgres server），负责在某台机器上监听端口（常见 5432）并处理请求。
pgAdmin 是客户端工具之一，它通过网络协议（PostgreSQL protocol）去连：host + port + 用户名 + 密码 + 数据库名。

所以 pgAdmin 自己不等于数据库，它不会“存”你的数据，它只是 帮你连、帮你发请求、帮你看结果。

这点和 pgcli 完全一样：pgAdmin / pgcli / psql 都是客户端。


* Just like with the Postgres container, we specify a network and a name for pgAdmin.
* The container names (`pgdatabase` and `pgadmin`) allow the containers to find each other within the network.


## Connect pgAdmin to PostgreSQL

You should now be able to load pgAdmin on a web browser by browsing to `http://localhost:8085`. Use the same email and password you used for running the container to log in.

1. Open browser and go to `http://localhost:8085`
2. Login with email: `admin@admin.com`, password: `root`
3. Right-click "Servers" → Register → Server
4. Configure:
   - **General tab**: Name: `Local Docker`
   - **Connection tab**:
     - Host: `pgdatabase` (the container name)
     - Port: `5432`
     - Username: `root`
     - Password: `root`
5. Save

Now you can explore the database using the pgAdmin interface!


# Docker Composer
`docker-compose` allows us to launch multiple containers using a single configuration file, so that we don't have to run multiple complex `docker run` commands separately.

Docker compose makes use of YAML files. Here's the `docker-compose.yaml` file:

```yaml
services:
  pgdatabase:
    image: postgres:18
    environment:
      POSTGRES_USER: "root"
      POSTGRES_PASSWORD: "root"
      POSTGRES_DB: "ny_taxi"
    volumes:
      - "ny_taxi_postgres_data:/var/lib/postgresql"
    ports:
      - "5432:5432"

  pgadmin:
    image: dpage/pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: "admin@admin.com"
      PGADMIN_DEFAULT_PASSWORD: "root"
    volumes:
      - "pgadmin_data:/var/lib/pgadmin"
    ports:
      - "8085:80"



volumes:
  ny_taxi_postgres_data:
  pgadmin_data:
```

### Explanation

* We don't have to specify a network because `docker compose` takes care of it: every single container (or "service", as the file states) will run within the same network and will be able to find each other according to their names (`pgdatabase` and `pgadmin` in this example).
* All other details from the `docker run` commands (environment variables, volumes and ports) are mentioned accordingly in the file following YAML syntax.

## Start Services with Docker Compose

We can now run Docker compose by running the following command from the same directory where `docker-compose.yaml` is found. Make sure that all previous containers aren't running anymore:

```bash
docker-compose up
```

### Detached Mode

If you want to run the containers again in the background rather than in the foreground (thus freeing up your terminal), you can run them in detached mode:

```bash
docker-compose up -d
```

## Stop Services

You will have to press `Ctrl+C` in order to shut down the containers when running in foreground mode. The proper way of shutting them down is with this command:

```bash
docker-compose down
```

## Other Useful Commands

```bash
# View logs
docker-compose logs

# Stop and remove volumes
docker-compose down -v
```

## Benefits of Docker Compose

- Single command to start all services
- Automatic network creation
- Easy configuration management
- Declarative infrastructure

## Running the Ingestion Script with Docker Compose

If you want to re-run the dockerized ingest script when you run Postgres and pgAdmin with `docker compose`, you will have to find the name of the virtual network that Docker compose created for the containers.

```bash
# check the network link:
docker network ls

# it's pipeline_default (or similar based on directory name)
# now run the script:
docker run -it --rm\
  --network=pipeline_default \
  taxi_ingest:v001 \
    --pg_user=root \
    --pg_password=root \
    --pg_host=pgdatabase \
    --pg_port=5432 \
    --pg_db=ny_taxi \
    --target_table=yellow_taxi_trips
```



# Cleanup
When you're done with the workshop, clean up Docker resources to free up disk space.

## Stop All Running Containers

```bash
docker-compose down
```

## Remove Specific Containers

```bash
# List all containers
docker ps -a

# Remove specific container
docker rm <container_id>

# Remove all stopped containers
docker container prune
```

## Remove Docker Images

```bash
# List all images
docker images

# Remove specific image
docker rmi taxi_ingest:v001

# Remove all unused images
docker image prune -a
```

## Remove Docker Volumes

```bash
# List volumes
docker volume ls

# Remove specific volumes
docker volume rm ny_taxi_postgres_data
docker volume rm pgadmin_data

# Remove all unused volumes
docker volume prune
```

## Remove Docker Networks

```bash
# List networks
docker network ls

# Remove specific network
docker network rm pg-network

# Remove all unused networks
docker network prune
```

## Complete Cleanup

Removes ALL Docker resources - use with caution!

```bash
# ⚠️ Warning: This removes ALL Docker resources!
docker system prune -a --volumes
```

## Clean Up Local Files

```bash
# Remove parquet files
rm *.parquet

# Remove Python cache
rm -rf __pycache__ .pytest_cache

# Remove virtual environment (if using venv)
rm -rf .venv
```

---
