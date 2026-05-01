FROM mcr.microsoft.com/playwright/python:v1.58.0-jammy

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Install Playwright Python package (ships its own CLI for browser install)
RUN pip install --no-cache-dir playwright==1.58.0

# Install Chromium browser and its system dependencies
RUN playwright install --with-deps chromium

# Run the Playwright browser server
CMD ["playwright", "run-server", "--port", "3000"]
