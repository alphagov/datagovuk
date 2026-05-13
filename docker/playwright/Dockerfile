FROM mcr.microsoft.com/playwright/python:v1.59.0-jammy

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

RUN --mount=type=cache,target=/root/.cache/pip pip install playwright==1.59.0

RUN --mount=type=cache,target=/ms-playwright playwright install --with-deps chromium

CMD ["playwright", "run-server", "--port", "3000"]
