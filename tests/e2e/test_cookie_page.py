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
def test_cookie_page_accept(lazy_page, get_cookie, live_server_url) -> None:
    lazy_page.goto(live_server_url)
    assert (
        get_cookie("cookies_policy", lazy_page)["value"]
        == '{"essential":true,"settings":false,"usage":false,"campaigns":false}'
    )
    assert get_cookie("cookies_preferences_set", lazy_page) is None
    expect(lazy_page.get_by_role("link", name="Cookies", exact=True)).to_be_visible()
    lazy_page.get_by_role("link", name="Cookies", exact=True).click()
    lazy_page.get_by_role("radio", name="Use cookies that measure my website use", exact=True).check()
    lazy_page.get_by_role(
        "radio",
        name="Do not use cookies that help with communications and marketing",
        exact=True,
    ).check()
    lazy_page.get_by_role("radio", name="Use cookies that remember my settings on the site", exact=True).check()
    lazy_page.get_by_role("button", name="Save changes").click()
    expect(lazy_page.get_by_text("Your cookie settings were")).to_be_visible()
    lazy_page.get_by_role("link", name="Go back to the page you were").click()
    assert (
        get_cookie("cookies_policy", lazy_page)["value"]
        == '{"essential":true,"settings":true,"usage":true,"campaigns":false}'
    )
    assert get_cookie("cookies_preferences_set", lazy_page)["value"] == "true"


@pytest.mark.parametrize(
    "lazy_page",
    [
        lf("page"),
        lf("mobile_page"),
    ],
)
def test_cookie_page_refuse(lazy_page, get_cookie, live_server_url) -> None:
    lazy_page.goto(live_server_url)
    assert (
        get_cookie("cookies_policy", lazy_page)["value"]
        == '{"essential":true,"settings":false,"usage":false,"campaigns":false}'
    )
    assert get_cookie("cookies_preferences_set", lazy_page) is None
    expect(lazy_page.get_by_role("link", name="Cookies", exact=True)).to_be_visible()
    lazy_page.get_by_role("link", name="Cookies", exact=True).click()
    lazy_page.get_by_role("radio", name="Do not use cookies that measure my website use", exact=True).check()
    lazy_page.get_by_role(
        "radio",
        name="Do not use cookies that help with communications and marketing",
        exact=True,
    ).check()
    lazy_page.get_by_role("radio", name="Do not use cookies that remember my settings on the site", exact=True).check()
    lazy_page.get_by_role("button", name="Save changes").click()
    expect(lazy_page.get_by_text("Your cookie settings were")).to_be_visible()
    lazy_page.get_by_role("link", name="Go back to the page you were").click()
    assert (
        get_cookie("cookies_policy", lazy_page)["value"]
        == '{"essential":true,"settings":false,"usage":false,"campaigns":false}'
    )
    assert get_cookie("cookies_preferences_set", lazy_page)["value"] == "true"


@pytest.mark.parametrize(
    "lazy_page",
    [
        lf("page"),
        lf("mobile_page"),
    ],
)
def test_cookie_page_default_refuse(lazy_page, get_cookie, live_server_url) -> None:
    lazy_page.goto(live_server_url)
    assert (
        get_cookie("cookies_policy", lazy_page)["value"]
        == '{"essential":true,"settings":false,"usage":false,"campaigns":false}'
    )
    assert get_cookie("cookies_preferences_set", lazy_page) is None
    expect(lazy_page.get_by_role("link", name="Cookies", exact=True)).to_be_visible()
    lazy_page.get_by_role("link", name="Cookies", exact=True).click()
    lazy_page.get_by_role("button", name="Save changes").click()
    expect(lazy_page.get_by_text("Your cookie settings were")).to_be_visible()
    lazy_page.get_by_role("link", name="Go back to the page you were").click()
    assert (
        get_cookie("cookies_policy", lazy_page)["value"]
        == '{"essential":true,"settings":false,"usage":false,"campaigns":false}'
    )
    assert get_cookie("cookies_preferences_set", lazy_page)["value"] == "true"
