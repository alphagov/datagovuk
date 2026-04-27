from django.urls import reverse
from playwright.sync_api import expect


def test_not_found_page(page, live_server_url):
    page.goto(live_server_url + "/not-found")
    expect(page.get_by_role("heading", level=1)).to_have_text("Page not found")


def test_bad_request_page(page, live_server_url):
    page.goto(live_server_url + reverse("pages:error_400_test"))
    expect(page.get_by_role("heading", level=1)).to_have_text("Bad request")


def test_forbidden_page(page, live_server_url):
    page.goto(live_server_url + reverse("pages:error_403_test"))
    expect(page.get_by_role("heading", level=1)).to_have_text("Forbidden")


def test_server_error_page(page, live_server_url):
    page.goto(live_server_url + reverse("pages:error_500_test"))
    expect(page.get_by_role("heading", level=1)).to_have_text("Sorry, there is a problem with the service")
