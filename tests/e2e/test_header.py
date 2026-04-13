from playwright.sync_api import expect


def test_header(page, live_server_url) -> None:
    page.goto(live_server_url)
    expect(page.get_by_role("link", name="Home")).to_be_visible()
    expect(page.get_by_role("button", name="Collections")).to_be_visible()
    expect(page.get_by_role("button", name="Data manual")).to_be_visible()
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
    # Expect data manual link to only be visible after clicking Data Manual sub-menu
    expect(page.get_by_role("link", name="Who this manual is for")).not_to_be_visible()
    page.get_by_role("button", name="Data manual").click()
    expect(page.get_by_role("link", name="Who this manual is for")).to_be_visible()
    expect(page.get_by_role("link", name="Data management")).to_be_visible()
    expect(page.get_by_role("link", name="Data standards", exact=True)).to_be_visible()
    expect(page.get_by_role("link", name="Security")).to_be_visible()
    expect(page.get_by_role("link", name="Data protection and privacy")).to_be_visible()
    expect(page.get_by_role("link", name="Data sharing")).to_be_visible()
    expect(page.get_by_role("link", name="AI and data-driven technologies")).to_be_visible()
    expect(page.get_by_role("link", name="APIs and technical guidance")).to_be_visible()
    expect(page.get_by_role("link", name="General guidance")).to_be_visible()
    expect(page.get_by_role("link", name="Tell us what you think")).to_be_visible()
    expect(page.get_by_role("link", name="Join a data community")).to_be_visible()


def test_header_mobile(mobile_page, live_server_url) -> None:
    mobile_page.goto(live_server_url)
    expect(mobile_page.get_by_role("link", name="Home")).to_be_visible()
    expect(mobile_page.get_by_role("button", name="Menu")).to_be_visible()
    # Expect link to only be visible after clicking Menu
    expect(
        mobile_page.locator("#datagovuk-menu-collections").get_by_role("link", name="Business and economy"),
    ).not_to_be_visible()
    expect(mobile_page.get_by_role("link", name="Who this manual is for")).not_to_be_visible()
    mobile_page.get_by_role("button", name="Menu").click()
    expect(
        mobile_page.locator("#datagovuk-menu-collections").get_by_role("link", name="Business and economy"),
    ).to_be_visible()
    expect(mobile_page.get_by_role("link", name="Who this manual is for")).to_be_visible()
    expect(mobile_page.get_by_role("banner").get_by_role("link", name="Directory")).to_be_visible()
