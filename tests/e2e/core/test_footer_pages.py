import pytest
from playwright.sync_api import expect


@pytest.mark.smoke
def test_footer_pages(page, live_server_url):
    footer_links = {
        "Roadmap": "/roadmap/",
        "About": "/about/",
        "Support": "/support/",
        "Accessibility": "/accessibility/",
        "Cookies": "/cookies/",
        "Privacy and terms": "/privacy-and-terms/",
    }

    page.goto(live_server_url)
    for name, href in footer_links.items():
        link = page.get_by_role("link", name=name, exact=True)
        expect(link).to_have_attribute("href", href)
        link.click()
        expect(page).to_have_url(live_server_url + href)
