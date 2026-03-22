# # containerize the script. Create the following Dockerfile file:

# # base Docker image that we will build on
# FROM python:3.13.11-slim

# # set up our image by installing prerequisites; pandas in this case
# RUN pip install pandas pyarrow

# # set up the working directory inside the container
# WORKDIR /app
# # copy the script to the container. 1st name is source file, 2nd is destination
# COPY pipeline.py pipeline.py

# # define what to do first when the container runs
# # in this example, we will just run the script
# ENTRYPOINT ["python", "pipeline.py"]

# # so you can just run `docker run -it --rm test:pandas 12`


# # Let's build the image:
# # docker build -t test:pandas .

# =====================================with uv ========================
# Start with slim Python 3.13 image
FROM python:3.13.10-slim

# Copy uv binary from official uv image (multi-stage build pattern)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/
# 它不是从本地拷，也不是从当前构建上下文拷，而是 从另一个镜像里拷。

# ghcr.io/astral-sh/uv:latest 是一个镜像（托管在 GitHub Container Registry）

# Docker 会把这个镜像当作“来源”，从它的文件系统里取出 /uv


# Set working directory
WORKDIR /code


# Add virtual environment to PATH so we can use installed packages
ENV PATH="/code/.venv/bin:$PATH"

# Copy dependency files first (better layer caching)
COPY "pyproject.toml" "uv.lock" ".python-version" ./
# Install dependencies from lock file (ensures reproducible builds)
RUN uv sync --locked
# only sync with "main" dependencies in pyproject.toml

# Copy application code
COPY ingest_data.py ingest_data.py

# Set entry point
ENTRYPOINT ["uv", "run", "python", "ingest_data.py"]
