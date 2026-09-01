from playwright.sync_api import expect


def test_survey_banner_visible_on_load(page, live_server_url) -> None:
    page.goto(live_server_url)
    expect(page.get_by_text("Help us improve the National Data Library")).to_be_visible()


def test_survey_banner_dismiss(page, get_cookie, live_server_url) -> None:
    page.goto(live_server_url)
    page.get_by_role("button", name="Accept additional cookies").click()
    expect(page.get_by_text("Help us improve the National Data Library")).to_be_visible()
    page.locator(".datagovuk-close").click()
    expect(page.get_by_text("Help us improve the National Data Library")).not_to_be_visible()
    assert get_cookie("survey_banner_dismissed_2026_07", page)["value"] == "true"


def test_survey_banner_stays_hidden_after_dismiss_and_page_refresh(page, get_cookie, live_server_url) -> None:
    page.goto(live_server_url)
    page.get_by_role("button", name="Accept additional cookies").click()
    page.locator(".datagovuk-close").click()
    page.goto(live_server_url)
    expect(page.get_by_text("Help us improve the National Data Library")).not_to_be_visible()
    assert get_cookie("survey_banner_dismissed_2026_07", page)["value"] == "true"


def test_survey_banner_dismiss_without_accepting_cookies(page, get_cookie, live_server_url) -> None:
    page.goto(live_server_url)
    expect(page.get_by_text("Help us improve the National Data Library")).to_be_visible()
    page.locator(".datagovuk-close").click()
    expect(page.get_by_text("Help us improve the National Data Library")).not_to_be_visible()
    assert get_cookie("survey_banner_dismissed_2026_07", page)["value"] == "true"
    page.goto(live_server_url)
    expect(page.get_by_text("Help us improve the National Data Library")).not_to_be_visible()


def test_no_cookie_for_survey_banner_when_all_cookies_rejected(page, get_cookie, live_server_url) -> None:
    page.goto(live_server_url)
    page.get_by_role("button", name="Reject additional cookies").click()
    page.locator(".datagovuk-close").click()
    expect(page.get_by_text("Help us improve the National Data Library")).not_to_be_visible()
    assert get_cookie("survey_banner_dismissed_2026_07", page)["value"] == "true"
    page.goto(live_server_url)
    expect(page.get_by_text("Help us improve the National Data Library")).not_to_be_visible()
