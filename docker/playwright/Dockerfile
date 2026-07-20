FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

RUN --mount=type=cache,target=/root/.cache/pip pip install playwright==1.61.0

RUN playwright install --with-deps chromium

CMD ["playwright", "run-server", "--port", "3000", "--host", "0.0.0.0"]
