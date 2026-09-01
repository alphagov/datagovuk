FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system playwright

RUN playwright install --with-deps chromium

CMD ["playwright", "run-server", "--port", "3000", "--host", "0.0.0.0"]
