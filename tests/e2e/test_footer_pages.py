from playwright.sync_api import expect


def test_footer_pages(page, live_server_url):
    footer_links = {
        "Roadmap": "/roadmap/",
        "About": "/about/",
        "Support": "/support/",
        "Accessibility": "/accessibility/",
        "Cookies": "/cookies/",
        "Privacy and terms": "/privacy-and-terms/",
        "data.gov.uk team": "/team/",
    }

    page.goto(live_server_url)
    for name, href in footer_links.items():
        link = page.get_by_role("link", name=name, exact=True)
        expect(link).to_have_attribute("href", href)
        link.click()
        expect(page).to_have_url(live_server_url + href)


def test_about_page_content(page, live_server_url):
    page.goto(live_server_url + "/about/")

    expect(page.get_by_role("heading", level=1)).to_have_text("About data.gov.uk")
    expect(
        page.get_by_role("heading", level=2, name="Changes to the previous data.gov.uk functionality"),
    ).to_be_visible()

    body = page.locator(".datagovuk-content")
    collections_link = body.get_by_role("link", name="collections", exact=True)
    expect(collections_link).to_have_attribute("href", "/")

    collections_link.click()
    expect(page).to_have_url(live_server_url + "/")


def test_accessibility_page_content(page, live_server_url):
    page.goto(live_server_url + "/accessibility/")
    expect(page.get_by_role("heading", level=1)).to_have_text("Accessibility statement for data.gov.uk")
    expect(page.get_by_role("heading", level=2, name="How accessible this website is")).to_be_visible()
    expect(page.get_by_role("heading", level=2, name="Feedback and contact information")).to_be_visible()
    expect(page.get_by_role("link", name="AbilityNet")).to_have_attribute("href", "https://mcmw.abilitynet.org.uk/")
    expect(page.get_by_role("link", name="Web Content Accessibility Guidelines version 2.2")).to_have_attribute(
        "href",
        "https://www.w3.org/TR/WCAG22/",
    )


def test_support_page_content(page, live_server_url):
    page.goto(live_server_url + "/support/")
    expect(page.get_by_role("heading", level=1)).to_have_text("Support")
    expect(page.get_by_role("heading", level=2, name="If you’re a civil servant")).to_be_visible()  # noqa: RUF001
    expect(page.get_by_role("heading", level=2, name="Other requests")).to_be_visible()
    expect(page.get_by_role("link", name="#datagovuk")).to_have_attribute(
        "href",
        "https://ukgovernmentdigital.slack.com/archives/C037J3GTE4T",
    )


def test_team_page_content(page, live_server_url):
    page.goto(live_server_url + "/team/")
    expect(page.get_by_role("heading", level=1)).to_have_text("data.gov.uk team")
    expect(page.get_by_role("link", name="#datagovuk")).to_have_attribute(
        "href",
        "https://ukgovernmentdigital.slack.com/archives/C037J3GTE4T",
    )
    expect(page.get_by_role("heading", level=2, name="Team members")).to_be_visible()


def test_privacy_and_terms_page_content(page, live_server_url):
    page.goto(live_server_url + "/privacy-and-terms/")
    expect(page.get_by_role("heading", level=1)).to_have_text("Privacy and terms")
    expect(page.get_by_role("heading", level=2, name="Terms of use", exact=True)).to_be_visible()
    expect(page.get_by_role("heading", level=3, name="Who we are")).to_be_visible()
    expect(page.get_by_role("heading", level=3, name="Responsibility for datasets")).to_be_visible()
    expect(page.get_by_role("link", name="gds.data.protection@dsit.gov.uk")).to_have_attribute(
        "href",
        "mailto:gds.data.protection@dsit.gov.uk",
    )


def test_roadmap_page_content(page, live_server_url):
    page.goto(live_server_url + "/roadmap/")
    expect(page.get_by_role("heading", level=1)).to_have_text("Our plan for data.gov.uk")
    expect(page.get_by_role("heading", level=2, name="data.gov.uk roadmap")).to_be_visible()
    expect(page.get_by_role("heading", level=3, name="Now")).to_be_visible()
    expect(page.get_by_role("link", name="Complete the feedback form").first).to_have_attribute(
        "href",
        "https://forms.office.com/e/9V26PNFQaR",
    )
    collections_link = page.get_by_role("link", name="data collections pages", exact=True)
    expect(collections_link).to_have_attribute("href", "/")
    collections_link.click()
    expect(page).to_have_url(live_server_url + "/")
