export COMPOSE_FILE := "docker-compose.local.yml"


# Default command to list all available commands.
default:
    @just --list

# build: Build python image.
build *args:
    @echo "Building python image..."
    @docker compose build {{args}}

# up: Start up containers.
up *args:
    @echo "Starting up containers..."
    @docker compose up -d --remove-orphans {{args}}

# down: Stop containers.
down:
    @echo "Stopping containers..."
    @docker compose down

# prune: Remove containers and their volumes.
prune *args:
    @echo "Killing containers and removing volumes..."
    @docker compose down -v {{args}}

# logs: View container logs
logs *args:
    @docker compose logs -f {{args}}

# manage: Executes `manage.py` command.
manage +args:
    @docker compose run --rm django python ./manage.py {{args}}

bash:
    @docker compose run --rm django bash

# test: Run pytest
test *args:
    @docker compose run --rm django pytest {{args}}

# show-trace: show a playwright trace
show-trace +args:
    uv run playwright show-trace {{args}}

# install-playwright: Install playwright locally
install-playwright:
    uv run playwright install --with-deps

# e2e-codegen: Generate a new end to end test with playwright recorder
e2e-codegen +args:
    uv run playwright codegen --target python-pytest -o tests/e2e/{{args}} 127.0.0.1:8000

# lint: Run pre-commit checks without the commit
lint:
    pre-commit run

# compress: Compress CSS/JS files referenced in templates with compress tags.  See https://github.com/django-compressor/django-compressor
compress:
    @docker compose run --rm django python ./manage.py compress --force --engine jinja2 --extension .jinja

# collectstatic: Collect static assets in to a single location for serving in non-local environments
collectstatic:
    @docker compose run --rm django python ./manage.py collectstatic
