import pytest
from playwright.sync_api import expect


def _test_links_work(page, live_server_url, click_menu) -> None:
    # Ensure directory link works
    page.get_by_role("banner").get_by_role("link", name="Directory").click()

    expect(page).to_have_url(live_server_url + "/search")
    page.goto(live_server_url)

    # Ensure Help works
    if click_menu:
        page.get_by_role("button", name="Menu").click()

    page.get_by_role("banner").get_by_role("link", name="Help").click()

    expect(page).to_have_url(live_server_url + "/help/")
    page.goto(live_server_url)


@pytest.mark.smoke
@pytest.mark.devices(["desktop"])
def test_header(page, live_server_url) -> None:
    page.goto(live_server_url)
    expect(page.get_by_role("link", name="Home")).to_be_visible()
    expect(page.get_by_role("button", name="Collections")).to_be_visible()
    expect(page.get_by_role("banner").get_by_role("link", name="Directory")).to_be_visible()
    header_collections_locator = page.locator("#datagovuk-menu-collections")
    # Expect collection link to only be visible after clicking Collections sub-menu
    collection_labels = [
        "Business and economy",
        "Environment",
        "Government",
        "Land and property",
        "People",
        "Transport",
    ]
    expect(
        header_collections_locator.get_by_role("link", name=collection_labels[0]),
    ).not_to_be_visible()
    for collection_label in collection_labels:
        page.get_by_role("button", name="Collections").click()
        expect(
            header_collections_locator.get_by_role("link", name=collection_label),
        ).to_be_visible()
        page.locator("#datagovuk-menu-collections").get_by_role("link", name=collection_label).click()
        expect(page.get_by_role("heading", name=collection_label)).to_be_visible()
        page.goto(live_server_url)

    _test_links_work(page, live_server_url, click_menu=False)


@pytest.mark.smoke
@pytest.mark.devices(["mobile"])
def test_header_mobile(page, live_server_url) -> None:
    page.goto(live_server_url)
    expect(page.get_by_role("link", name="Home")).to_be_visible()
    expect(page.get_by_role("button", name="Menu")).to_be_visible()
    # Expect link to only be visible after clicking Menu
    expect(
        page.locator("#datagovuk-menu-collections").get_by_role("link", name="Business and economy"),
    ).not_to_be_visible()
    page.get_by_role("button", name="Menu").click()
    expect(
        page.locator("#datagovuk-menu-collections").get_by_role("link", name="Business and economy"),
    ).to_be_visible()

    _test_links_work(page, live_server_url, click_menu=True)
