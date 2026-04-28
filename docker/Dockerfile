FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS python-build-stage

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0

ARG APP_HOME=/app

WORKDIR ${APP_HOME}

RUN apt-get update && apt-get install --no-install-recommends -y \
  build-essential

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev
COPY . ${APP_HOME}

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev


FROM python:3.14-slim-bookworm AS python-run-stage

ARG APP_HOME=/app
ARG GUNICORN_WORKERS=4
ARG GUNICORN_THREADS=4

WORKDIR ${APP_HOME}

RUN addgroup --system django \
  && adduser --system --ingroup django django

RUN apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

COPY --chown=django:django ./docker/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

# Copy the application from the builder
COPY --from=python-build-stage --chown=django:django ${APP_HOME} ${APP_HOME}

# make django owner of the WORKDIR directory as well.
RUN chown django:django ${APP_HOME}

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

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
