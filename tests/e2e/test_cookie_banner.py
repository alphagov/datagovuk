import pytest
from playwright.sync_api import expect
from pytest_lazy_fixtures import lf


@pytest.mark.parametrize(
    "lazy_page",
    [
        lf("page"),
        lf("mobile_page"),
    ],
)
def test_cookie_banner_accept(lazy_page, get_cookie, live_server_url) -> None:
    lazy_page.goto(live_server_url)
    assert (
        get_cookie("cookies_policy", lazy_page)["value"]
        == '{"essential":true,"settings":false,"usage":false,"campaigns":false}'
    )
    assert get_cookie("cookies_preferences_set", lazy_page) is None
    expect(lazy_page.get_by_role("heading", name="Cookies on data.gov.uk")).to_be_visible()
    lazy_page.get_by_role("button", name="Accept additional cookies").click()
    expect(lazy_page.get_by_text("You have accepted additional")).to_be_visible()
    lazy_page.get_by_role("button", name="Hide this message").click()
    lazy_page.goto(live_server_url)
    expect(lazy_page.get_by_role("heading", name="Cookies on data.gov.uk")).not_to_be_visible()
    assert (
        get_cookie("cookies_policy", lazy_page)["value"]
        == '{"essential":true,"settings":true,"usage":true,"campaigns":true}'
    )
    assert get_cookie("cookies_preferences_set", lazy_page)["value"] == "true"


@pytest.mark.parametrize(
    "lazy_page",
    [
        lf("page"),
        lf("mobile_page"),
    ],
)
def test_cookie_banner_reject(lazy_page, get_cookie, live_server_url) -> None:
    lazy_page.goto(live_server_url)
    assert (
        get_cookie("cookies_policy", lazy_page)["value"]
        == '{"essential":true,"settings":false,"usage":false,"campaigns":false}'
    )
    assert get_cookie("cookies_preferences_set", lazy_page) is None
    expect(lazy_page.get_by_role("heading", name="Cookies on data.gov.uk")).to_be_visible()
    lazy_page.get_by_role("button", name="Reject additional cookies").click()
    expect(lazy_page.get_by_text("You have rejected additional")).to_be_visible()
    lazy_page.get_by_role("button", name="Hide this message").click()
    lazy_page.goto(live_server_url)
    expect(lazy_page.get_by_role("heading", name="Cookies on data.gov.uk")).not_to_be_visible()
    assert (
        get_cookie("cookies_policy", lazy_page)["value"]
        == '{"essential":true,"settings":false,"usage":false,"campaigns":false}'
    )
    assert get_cookie("cookies_preferences_set", lazy_page)["value"] == "true"
