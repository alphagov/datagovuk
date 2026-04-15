import pytest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="class")
def live_server_url(request):
    server = StaticLiveServerTestCase
    server.setUpClass()
    return server.live_server_url


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


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
