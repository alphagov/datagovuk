import pytest
from playwright.sync_api import expect


def default_cookie_radio_selection(page) -> None:
    expect(page.get_by_role("radio", name="Do not use cookies that measure my website use", exact=True)).to_be_checked()
    expect(
        page.get_by_role("radio", name="Do not use cookies that help with communications and marketing", exact=True),
    ).to_be_checked()
    expect(
        page.get_by_role("radio", name="Do not use cookies that remember my settings on the site", exact=True),
    ).to_be_checked()


@pytest.mark.smoke
def test_cookie_page_accept(page, get_cookie, live_server_url) -> None:
    page.goto(live_server_url)
    assert (
        get_cookie("cookies_policy", page)["value"]
        == '{"essential":true,"settings":false,"usage":false,"campaigns":false}'
    )
    assert get_cookie("cookies_preferences_set", page) is None
    expect(page.get_by_role("link", name="Cookies", exact=True)).to_be_visible()
    page.get_by_role("link", name="Cookies", exact=True).click()

    default_cookie_radio_selection(page)

    page.get_by_role("radio", name="Use cookies that measure my website use", exact=True).check()
    page.get_by_role(
        "radio",
        name="Do not use cookies that help with communications and marketing",
        exact=True,
    ).check()
    page.get_by_role("radio", name="Use cookies that remember my settings on the site", exact=True).check()
    page.get_by_role("button", name="Save changes").click()
    expect(page.get_by_text("Your cookie settings were")).to_be_visible()
    page.get_by_role("link", name="Go back to the page you were").click()
    assert (
        get_cookie("cookies_policy", page)["value"]
        == '{"essential":true,"settings":true,"usage":true,"campaigns":false}'
    )
    assert get_cookie("cookies_preferences_set", page)["value"] == "true"


@pytest.mark.smoke
def test_cookie_page_refuse(page, get_cookie, live_server_url) -> None:
    page.goto(live_server_url)
    assert (
        get_cookie("cookies_policy", page)["value"]
        == '{"essential":true,"settings":false,"usage":false,"campaigns":false}'
    )
    assert get_cookie("cookies_preferences_set", page) is None
    expect(page.get_by_role("link", name="Cookies", exact=True)).to_be_visible()
    page.get_by_role("link", name="Cookies", exact=True).click()
    page.get_by_role("radio", name="Do not use cookies that measure my website use", exact=True).check()
    page.get_by_role(
        "radio",
        name="Do not use cookies that help with communications and marketing",
        exact=True,
    ).check()
    page.get_by_role("radio", name="Do not use cookies that remember my settings on the site", exact=True).check()
    page.get_by_role("button", name="Save changes").click()
    expect(page.get_by_text("Your cookie settings were")).to_be_visible()
    page.get_by_role("link", name="Go back to the page you were").click()
    assert (
        get_cookie("cookies_policy", page)["value"]
        == '{"essential":true,"settings":false,"usage":false,"campaigns":false}'
    )
    assert get_cookie("cookies_preferences_set", page)["value"] == "true"


@pytest.mark.smoke
def test_cookie_page_default_refuse(page, get_cookie, live_server_url) -> None:
    page.goto(live_server_url)
    assert (
        get_cookie("cookies_policy", page)["value"]
        == '{"essential":true,"settings":false,"usage":false,"campaigns":false}'
    )
    assert get_cookie("cookies_preferences_set", page) is None
    expect(page.get_by_role("link", name="Cookies", exact=True)).to_be_visible()
    page.get_by_role("link", name="Cookies", exact=True).click()

    default_cookie_radio_selection(page)

    page.get_by_role("button", name="Save changes").click()
    expect(page.get_by_text("Your cookie settings were")).to_be_visible()
    page.get_by_role("link", name="Go back to the page you were").click()
    assert (
        get_cookie("cookies_policy", page)["value"]
        == '{"essential":true,"settings":false,"usage":false,"campaigns":false}'
    )
    assert get_cookie("cookies_preferences_set", page)["value"] == "true"
