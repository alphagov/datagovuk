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

### Install docker desktop
https://docs.docker.com/desktop/setup/install/mac-install/

### Install justfile
`just` is a simple way to save/run project-specific commands.  It's an alternative to `make` and the devs go in to the differences on the project homepage; https://github.com/casey/just

```
brew install just
```

### Initialise with justfile

```
just init
```

### Bring up the project under docker

`just up`

The project should now be running and accessible at `http://localhost:8000/`

### Troubleshooting

The most common source of problems when running locally is when `.envs/local/.django` is missing something that is present in `.envs/local/.django.example` - check this first!

## Basic Commands

### Running tests with pytest

`just test` - runs the tests under docker

### View docker stack logs

`just logs`

### Rebuild the docker stack

`just build`

### Other common commands

`just` should list out other common commands in the project

## Docs
