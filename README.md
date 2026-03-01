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