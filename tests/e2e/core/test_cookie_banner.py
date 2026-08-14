from playwright.sync_api import expect


def test_cookie_banner_accept(page, get_cookie, live_server_url) -> None:
    page.goto(live_server_url)
    assert (
        get_cookie("cookies_policy", page)["value"]
        == '{"essential":true,"settings":false,"usage":false,"campaigns":false}'
    )
    assert get_cookie("cookies_preferences_set", page) is None
    expect(page.get_by_role("heading", name="Cookies on data.gov.uk")).to_be_visible()
    page.get_by_role("button", name="Accept additional cookies").click()
    expect(page.get_by_text("You have accepted additional")).to_be_visible()
    page.get_by_role("button", name="Hide this message").click()
    page.goto(live_server_url)
    expect(page.get_by_role("heading", name="Cookies on data.gov.uk")).not_to_be_visible()
    assert (
        get_cookie("cookies_policy", page)["value"]
        == '{"essential":true,"settings":true,"usage":true,"campaigns":true}'
    )
    assert get_cookie("cookies_preferences_set", page)["value"] == "true"


def test_cookie_banner_reject(page, get_cookie, live_server_url) -> None:
    page.goto(live_server_url)
    assert (
        get_cookie("cookies_policy", page)["value"]
        == '{"essential":true,"settings":false,"usage":false,"campaigns":false}'
    )
    assert get_cookie("cookies_preferences_set", page) is None
    expect(page.get_by_role("heading", name="Cookies on data.gov.uk")).to_be_visible()
    page.get_by_role("button", name="Reject additional cookies").click()
    expect(page.get_by_text("You have rejected additional")).to_be_visible()
    page.get_by_role("button", name="Hide this message").click()
    page.goto(live_server_url)
    expect(page.get_by_role("heading", name="Cookies on data.gov.uk")).not_to_be_visible()
    assert (
        get_cookie("cookies_policy", page)["value"]
        == '{"essential":true,"settings":false,"usage":false,"campaigns":false}'
    )
    assert get_cookie("cookies_preferences_set", page)["value"] == "true"
