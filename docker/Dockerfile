FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS python-build-stage

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0

ARG APP_HOME=/app

WORKDIR ${APP_HOME}

RUN apt-get update && apt-get install --no-install-recommends -y \
  build-essential

COPY pyproject.toml ${APP_HOME}
COPY uv.lock ${APP_HOME}

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev
COPY . ${APP_HOME}

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

RUN addgroup --system django \
  && adduser --system --ingroup django django

# make django owner of the WORKDIR directory as well.
RUN chown django:django ${APP_HOME}

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"


FROM python-build-stage AS python-run-production

ARG GUNICORN_WORKERS=4
ARG GUNICORN_THREADS=4

RUN apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

COPY --chown=django:django ./docker/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

# Fake env vars necessary for collectstatic and compress to run
ENV DJANGO_SECRET_KEY=fake
ENV SENTRY_DSN=https://public@sentry.example.com/1
RUN python /app/manage.py collectstatic --noinput
RUN python /app/manage.py compress --engine jinja2 --extension=jinja

USER django
RUN mkdir ${APP_HOME}/tmp/
ENV GUNICORN_WORKERS=${GUNICORN_WORKERS}
ENV GUNICORN_THREADS=${GUNICORN_THREADS}
ENV APP_HOME=${APP_HOME}

ENTRYPOINT ["/start"]


FROM python-build-stage AS python-run-dev

# we need to move the virtualenv outside of the $APP_HOME directory because it will be overriden by the docker compose mount
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0
ENV VIRTUAL_ENV=/opt/venv
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
RUN uv venv $VIRTUAL_ENV

# devcontainer dependencies and utils
RUN apt-get update && apt-get install --no-install-recommends -y \
  sudo git bash-completion nano ssh

# Create devcontainer user and add it to sudoers
RUN groupadd --gid 1000 dev-user \
  && useradd --uid 1000 --gid dev-user --shell /bin/bash --create-home dev-user \
  && echo dev-user ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/dev-user \
  && chmod 0440 /etc/sudoers.d/dev-user

COPY --from=python-build-stage ${APP_HOME}/.venv ${VIRTUAL_ENV}
# Requirements are installed here to ensure they will be cached.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

RUN --mount=type=cache,target=/root/.cache/uv \
    uv run playwright install --with-deps chromium

ENV PATH="/${VIRTUAL_ENV}/bin:$PATH"
ENV PYTHONPATH="${VIRTUAL_ENV}/lib/python3.14/site-packages"

COPY ./docker/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./docker/start-dev /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

ENTRYPOINT ["/entrypoint"]
