# data.gov.uk

data.gov.uk website.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

License: MIT

## Settings

Moved to [settings](https://cookiecutter-django.readthedocs.io/en/latest/1-getting-started/settings.html).

## Running locally

The following steps will explain how to run the application locally and get in to a state where pull requests can be opened to modify the project on github.
They assume a user using Mac OSX.

### Install uv

https://docs.astral.sh/uv/getting-started/installation/

```
brew install uv
```

### Install pre-commit
```
uv tool install pre-commit --with pre-commit-uv
```
Ensure that `which pre-commit` resolves to point to the installed pre-commit executable - you may need to set your `$PATH` variable on the profile of your shell of choice.
```
pre-commit install
```

### Install docker desktop
https://docs.docker.com/desktop/setup/install/mac-install/

### Install justfile
`just` is a simple way to save/run project-specific commands.  It's an alternative to `make` and the devs go in to the differences on the project homepage; https://github.com/casey/just

```
brew install just
```

### Bring up the project under docker

`just up`

The project should now be running and accessible at `http://localhost:8000/`

## Basic Commands

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    uv run coverage run -m pytest
    uv run coverage html
    uv run open htmlcov/index.html

#### Running tests with pytest

    uv run pytest

### Sentry

Sentry is an error logging aggregator service. You can sign up for a free account at <https://sentry.io/signup/?code=cookiecutter> or download and host it yourself.
The system is set up with reasonable defaults, including 404 logging and integration with the WSGI application.

You must set the DSN url in production.

## Deployment

The following details how to deploy this application.

### Heroku

See detailed [cookiecutter-django Heroku documentation](https://cookiecutter-django.readthedocs.io/en/latest/3-deployment/deployment-on-heroku.html).

### Docker

See detailed [cookiecutter-django Docker documentation](https://cookiecutter-django.readthedocs.io/en/latest/3-deployment/deployment-with-docker.html).
