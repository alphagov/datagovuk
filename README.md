# data.gov.uk

data.gov.uk website.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

License: MIT

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

### Environment variables

Local environment variables are committed to the repository in `.envs/.local/.django`
and are therefore shared between the development team.

You can override environment variables for your local copy by editing `.envs/.local/.django-overrides`.
This allows developers to customise their local `datagovuk` instance e.g. with
custom feature flags and other settings (e.g. `GOOGLE_TAG_MANAGER_ID`, `ALLOWED_HOSTS`)

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

Developer docs are located in `docs/`.

## Related repositories

There are a number of other github repositories in use by the datagovuk team, including;

### Application

| Repository | Description |
| --- | --- |
| [ckanext-datagovuk](https://github.com/alphagov/ckanext-datagovuk) | The CKAN extension for data.gov.uk |
| [datagovuk-indexer](https://github.com/alphagov/datagovuk-indexer) | data.gov.uk opensearch indexer. |

### Infrastructure

| Repository | Description |
| --- | --- |
| [govuk-dgu-charts](https://github.com/alphagov/govuk-dgu-charts) | Helm charts for data.gov.uk's EKS deployment. |
| [govuk-fastly](https://github.com/alphagov/govuk-fastly/tree/main/datagovuk) | Fastly configs for gov.uk (including data.gov.uk) |
| [datagovuk-infrastructure](https://github.com/alphagov/datagovuk-infrastructure) | Terraform infrastructure-as-code for data.gov.uk AWS environments. Building to supersede govuk-dgu-charts. |

### Other

| Repository | Description |
| --- | --- |
| [datagovuk-scripts](https://github.com/alphagov/datagovuk-scripts) | A collection of datagovuk scripts that are run ad-hoc on local machines or on a container. |
| [datagovuk-experiments](https://github.com/alphagov/datagovuk-experiments) | A repository for experiments relating to data.gov.uk. |
| [datagovuk-sandbox](https://github.com/alphagov/datagovuk-sandbox) | A Flask prototyping app for data.gov.uk ideas. |
| [datagovuk-support](https://github.com/alphagov/datagovuk-support) | A repository to record one-off support tasks for data.gov.uk and related services. |
