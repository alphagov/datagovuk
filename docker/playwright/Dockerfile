FROM mcr.microsoft.com/playwright/python:v1.58.0-jammy

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

RUN pip install --no-cache-dir playwright==1.58.0

RUN playwright install --with-deps chromium

CMD ["playwright", "run-server", "--port", "3000"]
