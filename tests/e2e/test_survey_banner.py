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
def test_survey_banner_visible_on_load(lazy_page, live_server_url) -> None:
    lazy_page.goto(live_server_url)
    expect(lazy_page.get_by_text("Help us improve the National Data Library")).to_be_visible()


@pytest.mark.parametrize(
    "lazy_page",
    [
        lf("page"),
        lf("mobile_page"),
    ],
)
def test_survey_banner_dismiss(lazy_page, get_cookie, live_server_url) -> None:
    lazy_page.goto(live_server_url)
    expect(lazy_page.get_by_text("Help us improve the National Data Library")).to_be_visible()
    lazy_page.locator(".datagovuk-close").click()
    expect(lazy_page.get_by_text("Help us improve the National Data Library")).not_to_be_visible()
    assert get_cookie("survey_banner_dismissed_2026_07", lazy_page)["value"] == "true"


@pytest.mark.parametrize(
    "lazy_page",
    [
        lf("page"),
        lf("mobile_page"),
    ],
)
def test_survey_banner_stays_hidden_after_dismiss(lazy_page, get_cookie, live_server_url) -> None:
    lazy_page.goto(live_server_url)
    lazy_page.locator(".datagovuk-close").click()
    lazy_page.goto(live_server_url)
    expect(lazy_page.get_by_text("Help us improve the National Data Library")).not_to_be_visible()
    assert get_cookie("survey_banner_dismissed_2026_07", lazy_page)["value"] == "true"
