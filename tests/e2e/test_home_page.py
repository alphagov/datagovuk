from playwright.sync_api import expect

COLLECTIONS = {
    "Business and economy": "/collections/business-and-economy",
    "Environment": "/collections/environment",
    "Government": "/collections/government",
    "Land and property": "/collections/land-and-property",
    "People": "/collections/people",
    "Transport": "/collections/transport",
}


def test_homepage_heading(page, live_server_url):
    page.goto(live_server_url)
    main_content = page.locator(".datagovuk-main")
    expect(main_content.get_by_role("heading", level=1)).to_have_text(
        "The home of UK public data to inform decisions and build services",
    )


def test_homepage_has_cache_control_header_set(page, live_server_url):
    response = page.goto(live_server_url)
    cache_control = response.headers.get("cache-control")
    assert cache_control == "max-age=1800, public"


def test_homepage_collections_links(page, live_server_url):
    page.goto(live_server_url)
    collection_items = page.locator(".datagovuk-home-collections__items")
    for name, href in COLLECTIONS.items():
        link = collection_items.get_by_role("link", name=name, exact=True)
        expect(link).to_have_attribute("href", href)


def test_homepage_card_links(page, live_server_url):
    page.goto(live_server_url)
    expect(page.locator("#main").get_by_role("link", name="Data manual")).to_be_visible()
    expect(page.locator("#main").get_by_role("link", name="Directory")).to_be_visible()


def test_footer_links_have_correct_hrefs(page, live_server_url):
    page.goto(live_server_url)
    expect(page.get_by_role("link", name="Roadmap")).to_have_attribute(
        "href",
        "/roadmap/",
    )
    expect(page.get_by_role("link", name="About", exact=True)).to_have_attribute(
        "href",
        "/about/",
    )
    expect(page.get_by_role("link", name="Support", exact=True)).to_have_attribute(
        "href",
        "/support/",
    )
    expect(page.get_by_role("link", name="Accessibility")).to_have_attribute(
        "href",
        "/accessibility/",
    )
    expect(page.get_by_role("link", name="Cookies", exact=True)).to_have_attribute(
        "href",
        "/cookies/",
    )
    expect(page.get_by_role("link", name="Privacy and terms")).to_have_attribute(
        "href",
        "/privacy-and-terms/",
    )
    expect(page.get_by_role("link", name="data.gov.uk team", exact=True)).to_have_attribute(
        "href",
        "/team/",
    )
