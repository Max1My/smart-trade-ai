# Sample app

# Commands

...

# Prerequisites

## Virtualenv (optionally)

Poetry can work with an existing virtualenv (and can also be installed directly in a virtual env)
More information: https://poetry.eustace.io/docs/basic-usage/#poetry-and-virtualenvs

```shell
python3.12 -m venv .venv
. .venv/bin/activate
```

## Install Poetry (optionally)

https://python-poetry.org/docs/

Add poetry export plugin

```shell
poetry self add poetry-plugin-export
```

_Especially on Windows, self add and self remove may be problematic so that other methods should be preferred._

https://python-poetry.org/docs/plugins/#using-plugins

## Install dependencies

```shell
poetry install
```

Useful commands:

```shell
# Add base dependency
poetry add pendulum

# Add dev dependency
poetry add pendulum --group dev

# Update dependencies
poetry update

# Lock (without installing) the dependencies
poetry lock
```

## Install pre-commit hooks

https://pre-commit.com/

```shell
pre-commit install
```

Run against all the files (optionally).

_It's usually a good idea to run the hooks against all the files when adding new hooks._

```shell
pre-commit run --all-files
```

## Copy and modify local envs

```shell
cp ./config/.env_sample ./config/.env
nano ./config/.env
```
