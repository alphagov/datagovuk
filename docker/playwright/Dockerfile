FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN apt update
RUN apt install libatomic1

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system $(grep -i '"playwright' pyproject.toml | tr -d '",')

RUN playwright install --with-deps chromium

CMD ["playwright", "run-server", "--port", "3000", "--host", "0.0.0.0"]
