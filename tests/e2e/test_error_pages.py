import pytest
from django.urls import reverse
from playwright.sync_api import expect


@pytest.mark.smoke
def test_not_found_page(page, live_server_url):
    page.goto(live_server_url + "/not-found")
    expect(page.get_by_role("heading", level=1)).to_have_text("Page not found")


@pytest.mark.smoke
def test_bad_request_page(page, live_server_url):
    page.goto(live_server_url + reverse("core:test_error_400"))
    expect(page.get_by_role("heading", level=1)).to_have_text("Bad request")


@pytest.mark.smoke
def test_forbidden_page(page, live_server_url):
    page.goto(live_server_url + reverse("core:test_error_403"))
    expect(page.get_by_role("heading", level=1)).to_have_text("Forbidden")


@pytest.mark.smoke
def test_server_error_page(page, live_server_url):
    page.goto(live_server_url + reverse("core:test_error_500"))
    expect(page.get_by_role("heading", level=1)).to_have_text("Sorry, there is a problem with the service")
