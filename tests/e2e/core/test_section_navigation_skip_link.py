import pytest
from playwright.sync_api import expect

MAX_TABS = 50


@pytest.mark.devices(["desktop"])
@pytest.mark.parametrize(
    "path",
    [
        "/collections/business-and-economy/uk-trade",
        "/data-manual/data-protection-and-privacy",
    ],
)
def test_section_navigation_skip_link_moves_focus_to_page_content(page, live_server_url, path):
    page.goto(live_server_url + path)
    skip_link = page.get_by_role("link", name="Skip to page content")

    # Tab through the page like a keyboard user until the section navigation skip link is reached
    for _ in range(MAX_TABS):
        page.keyboard.press("Tab")
        if skip_link.evaluate("element => element === document.activeElement"):
            break

    expect(skip_link).to_be_focused()

    page.keyboard.press("Enter")

    expect(page.locator("#datagovuk-page-content")).to_be_focused()
