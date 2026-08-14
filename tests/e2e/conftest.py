import os

import pytest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from datagovuk.directory.e2e_fixtures import create_e2e_fixtures, delete_e2e_fixtures

PLAYWRIGHT_HOST = os.getenv("PLAYWRIGHT_HOST", "127.0.0.1")
DOCKER_HOSTNAME = "django"
BASE_URL = os.getenv("BASE_URL")
E2E_BASIC_AUTH_USERNAME = os.getenv("E2E_BASIC_AUTH_USERNAME")
E2E_BASIC_AUTH_PASSWORD = os.getenv("E2E_BASIC_AUTH_PASSWORD")


@pytest.fixture
def live_server_url(request, settings):
    if BASE_URL:
        return BASE_URL.rstrip("/")
    server = StaticLiveServerTestCase
    if PLAYWRIGHT_HOST == "127.0.0.1":
        server.setUpClass()
        return server.live_server_url
    settings.ALLOWED_HOSTS = [DOCKER_HOSTNAME]
    # Can ignore ruff complaints here as we are running tests
    server.host = "0.0.0.0"  # noqa: S104
    server.setUpClass()
    return server.live_server_url.replace("0.0.0.0", DOCKER_HOSTNAME)  # noqa: S104


@pytest.fixture(scope="session", autouse=True)
def setup_suite():
    if BASE_URL:
        # Don't bother with any fixture creation if we are running E2E tests against
        # a remote environment
        yield
    else:
        create_e2e_fixtures()
        yield
        delete_e2e_fixtures()


@pytest.fixture(scope="session")
def browser(playwright):

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


def pytest_generate_tests(metafunc):
    """
    Automatically parameterize tests marked with @pytest.mark.devices(['desktop', 'mobile']).
    """
    if "device_name" in metafunc.fixturenames:
        marker = metafunc.definition.get_closest_marker("devices")
        devices = marker.args[0] if marker else ["mobile", "desktop"]  # default to both desktop and mobile
        metafunc.parametrize("device_name", devices, indirect=True)


@pytest.fixture
def device_name(request):
    return getattr(request, "param", "desktop")


@pytest.fixture
def browser_context_args(device_name, playwright):
    args = {}

    if E2E_BASIC_AUTH_USERNAME and E2E_BASIC_AUTH_PASSWORD:
        args["http_credentials"] = {
            "username": E2E_BASIC_AUTH_USERNAME,
            "password": E2E_BASIC_AUTH_PASSWORD,
        }

    if device_name == "mobile":
        args.update(playwright.devices["Pixel 5"])
    else:
        args["viewport"] = {"width": 1280, "height": 720}

    return args


@pytest.fixture
def page(browser, browser_context_args, request):
    context = browser.new_context(**browser_context_args)
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
def get_cookie():
    def _get_cookie(cookie_name, page):
        return next((c for c in page.context.cookies() if c["name"] == cookie_name), None)

    return _get_cookie
