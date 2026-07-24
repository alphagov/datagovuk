export COMPOSE_FILE := "docker-compose.local.yml"


# Default command to list all available commands.
default:
    @just --list

# init: Initialise core dependencies for working on datagovuk
init:
    @echo "Installing uv..."
    brew install uv
    @echo ""
    @echo "Installing pre-commit..."
    uv tool install pre-commit --with pre-commit-uv
    @echo ""
    @echo "Initialising pre-commit..."
    pre-commit install
    @echo ""
    @echo "Copying overrides envfile if target does not exist..."
    @test -f .envs/.local/.django-overrides || cp .envs/.local/.django-overrides.example .envs/.local/.django-overrides
    just patch-zscaler-ssl
    @echo ""
    @echo "datagovuk install is initialised for local development. Bringing up the containers with '$ just up'"
    just up

patch-zscaler-ssl:
    @if [ ! -f zscaler.pem ]; then \
        echo "Patching zscaler SSL..."; \
        openssl s_client -showcerts -connect www.google.com:443 </dev/null 2>/dev/null | awk '/BEGIN CERTIFICATE/,/END CERTIFICATE/' > zscaler.pem; \
        echo 'REQUESTS_CA_BUNDLE="/app/zscaler.pem"' >> .envs/.local/.django-overrides; \
        echo 'SSL_CERT_FILE="/app/zscaler.pem"' >> .envs/.local/.django-overrides; \
        echo 'MONKEYPATCH_ZSCALER_SSL=true' >> .envs/.local/.django-overrides; \
        echo "Patching complete."; \
    else \
        echo "zscaler.pem already present"; \
    fi

# build: Build python image.
build *args:
    @echo "Building python image..."
    GIT_SHA=$(git rev-parse HEAD) docker compose -f docker-compose.local.yml build {{args}}

# up: Start up containers.
up *args:
    @echo "Starting up containers..."
    GIT_SHA=$(git rev-parse HEAD) docker compose -f docker-compose.local.yml up -d --remove-orphans {{args}}

# down: Stop containers.
down  *args:
    @echo "Stopping containers..."
    @docker compose down {{args}}

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

# shell: Executes `manage.py shell` command.
shell:
    @docker compose run --rm django python ./manage.py shell

bash:
    @docker compose run --rm django bash

# test: Run pytest
test *args:
    @docker compose exec django pytest {{args}}

coverage:
    @docker compose exec django coverage run -m pytest datagovuk/
    @docker compose exec django coverage html

# e2e-install-playwright: Install playwright locally
e2e-install-playwright:
    uv sync
    uv run playwright install --with-deps

# e2e-codegen: Generate a new end to end test with playwright recorder
e2e-codegen +args:
    uv run playwright codegen --target python-pytest -o tests/e2e/{{args}} http://localhost:8000

# e2e-debug: Run e2e test in debug mode (local/host, no Docker)
# Requires: just e2e-install-playwright (one-time setup)
e2e-debug *args:
    PWDEBUG=1 uv run pytest {{args}}

# e2e-show-trace: show a playwright trace
e2e-show-trace +args:
    uv run playwright show-trace {{args}}

# lint: Run pre-commit checks without the commit
lint *args:
    pre-commit run {{args}}

# compress: Compress CSS/JS files referenced in templates with compress tags.  See https://github.com/django-compressor/django-compressor
compress:
    @docker compose run --rm django python ./manage.py compress --force --engine jinja2 --extension .jinja

# collectstatic: Collect static assets in to a single location for serving in non-local environments
collectstatic:
    @docker compose run --rm django python ./manage.py collectstatic

# Build production docker image
prod-build *args:
    @echo "Building production python image..."
    docker compose -f docker-compose.production.yml build --build-arg GIT_SHA=$(git rev-parse HEAD) {{args}}

# Bring up production docker container
prod-up *args:
    @echo "Starting up production containers..."
    docker compose -f docker-compose.production.yml up -d --remove-orphans {{args}}

# Bring down production docker container
prod-down *args:
    @echo "Stopping production containers..."
    docker compose -f docker-compose.production.yml down {{args}}
