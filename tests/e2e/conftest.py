import pytest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="class")
def live_server_url(request):
    server = StaticLiveServerTestCase
    server.setUpClass()
    # yield so teardown can happen
    return server.live_server_url


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


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()
