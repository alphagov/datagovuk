import os

import pytest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import sync_playwright

PLAYWRIGHT_HOST = os.getenv("PLAYWRIGHT_HOST", "127.0.0.1")
DOCKER_HOSTNAME = "django"


@pytest.fixture
def live_server_url(request, settings):
    server = StaticLiveServerTestCase
    if PLAYWRIGHT_HOST == "127.0.0.1":
        server.setUpClass()
        return server.live_server_url
    settings.ALLOWED_HOSTS = [DOCKER_HOSTNAME]
    # Can ignore ruff complaints here as we are running tests
    server.host = "0.0.0.0"  # noqa: S104
    server.setUpClass()
    return server.live_server_url.replace("0.0.0.0", DOCKER_HOSTNAME)  # noqa: S104


@pytest.fixture(scope="session")
def browser():
    playwright = sync_playwright().start()

    # If PLAYWRIGHT_HOST is set to something other than 127.0.0.1,
    # connect to a remote Playwright browser server (e.g. Docker container).
    # Otherwise use a local browser.
    if PLAYWRIGHT_HOST != "127.0.0.1":
        browser = playwright.chromium.connect(
            f"ws://{PLAYWRIGHT_HOST}:3000",
        )
    else:
        browser = playwright.chromium.launch(headless=True)

    yield browser
    browser.close()
    playwright.stop()


@pytest.fixture
def page(browser, request):
    context = browser.new_context()
    context.tracing.start(screenshots=True, snapshots=True)
    page = context.new_page()
    yield page
    if request.node.rep_call.failed:
        context.tracing.stop(path=f"e2e-failure-traces/trace-{request.node.name}.zip")
    else:
        context.tracing.stop()
    page.close()
    context.close()


@pytest.fixture
def mobile_page(page):
    page.set_viewport_size({"width": 390, "height": 844})
    return page


@pytest.fixture
def get_cookie():
    def _get_cookie(cookie_name, page):
        return next((c for c in page.context.cookies() if c["name"] == cookie_name), None)

    return _get_cookie
