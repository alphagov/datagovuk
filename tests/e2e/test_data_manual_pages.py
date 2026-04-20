import pytest
from django.urls import reverse
from playwright.sync_api import expect
from pytest_lazy_fixtures import lf

DATA_MANUAL_CONTENT_PAGES = {
    "Who this manual is for": "/data-manual/who-this-manual-is-for",
    "Data management": "/data-manual/data-management",
    "Data standards": "/data-manual/data-standards",
    "Security": "/data-manual/security",
    "Data protection and privacy": "/data-manual/data-protection-and-privacy",
    "Data sharing": "/data-manual/data-sharing",
    "AI and data-driven technologies": "/data-manual/ai-and-data-driven-technologies",
    "APIs and technical guidance": "/data-manual/apis-and-technical-guidance",
    "General guidance": "/data-manual/general-guidance",
}

DATA_MANUAL_OTHER_PAGES = {
    "Tell us what you think": "https://forms.office.com/e/9V26PNFQaR",
    "Join a data community": "/data-manual/join-a-data-community",
}

DATA_MANUAL_PAGES = {**DATA_MANUAL_CONTENT_PAGES, **DATA_MANUAL_OTHER_PAGES}


class TestDataManualHome:
    @pytest.mark.parametrize(
        "lazy_page",
        [
            lf("page"),
            lf("mobile_page"),
        ],
    )
    def test_heading(self, lazy_page, live_server_url):
        lazy_page.goto(live_server_url + reverse("data_manual:home"))
        content = lazy_page.locator(".datagovuk-main")
        expect(content.get_by_role("heading", level=1)).to_have_text(
            "Data manual",
        )

    @pytest.mark.parametrize(
        "lazy_page",
        [
            lf("page"),
            lf("mobile_page"),
        ],
    )
    @pytest.mark.parametrize(("name", "href"), DATA_MANUAL_PAGES.items())
    def test_links(self, lazy_page, live_server_url, name, href):
        lazy_page.goto(live_server_url + reverse("data_manual:home"))
        link = lazy_page.get_by_role("link", name=name, exact=True)
        expect(link).to_have_attribute("href", href)

    def test_feedback_link(self, page, live_server_url):
        page.goto(live_server_url + reverse("data_manual:home"))
        feedback = page.locator(".datagovuk-feedback-inset-text")
        expect(feedback.get_by_role("link", name="Give us feedback")).to_have_attribute(
            "href",
            "https://forms.office.com/e/9V26PNFQaR",
        )

    def test_tell_us_what_you_think_link(self, page, live_server_url):
        page.goto(live_server_url + reverse("data_manual:home"))
        data_manual_card = page.locator(".datagovuk-data-manual-card").first
        expect(data_manual_card.get_by_role("link", name="Tell us what you think")).to_have_attribute(
            "href",
            "https://forms.office.com/e/9V26PNFQaR",
        )


class TestDataManualPage:
    def test_join_our_community_link(self, page, live_server_url):
        page.goto(
            live_server_url
            + reverse("data_manual:data_manual_page", kwargs={"data_manual_name": "who-this-manual-is-for"}),
        )
        link = page.get_by_role("link", name="Join a data community")
        expect(link).to_have_attribute("href", "/data-manual/join-a-data-community")
        expect(link).not_to_have_class("datagovuk-section-navigation__item--selected")

    def test_tell_us_what_you_think_link_not_selected(self, page, live_server_url):
        page.goto(
            live_server_url
            + reverse("data_manual:data_manual_page", kwargs={"data_manual_name": "who-this-manual-is-for"}),
        )
        link = page.get_by_role("link", name="Tell us what you think")
        expect(link).to_have_attribute("href", "https://forms.office.com/e/9V26PNFQaR")
        expect(link).not_to_have_class("datagovuk-section-navigation__item--selected")

    @pytest.mark.parametrize(("name", "href"), DATA_MANUAL_PAGES.items())
    def test_side_nav_links(self, page, live_server_url, name, href):
        page.goto(
            live_server_url
            + reverse("data_manual:data_manual_page", kwargs={"data_manual_name": "who-this-manual-is-for"}),
        )
        link = page.get_by_role("link", name=name, exact=True)
        expect(link).to_have_attribute("href", href)

    @pytest.mark.parametrize(("name", "href"), DATA_MANUAL_PAGES.items())
    def test_side_nav_links_on_mobile(self, mobile_page, live_server_url, name, href):
        mobile_page.goto(
            live_server_url
            + reverse("data_manual:data_manual_page", kwargs={"data_manual_name": "who-this-manual-is-for"}),
        )
        pages_button = mobile_page.locator(".datagovuk-section-navigation__button")
        pages_button.click()
        link = mobile_page.get_by_role("link", name=name, exact=True)
        expect(link).to_be_visible()
        expect(link).to_have_attribute("href", href)

    def test_side_nav_selected(self, page, live_server_url):
        page.goto(
            live_server_url + reverse("data_manual:data_manual_page", kwargs={"data_manual_name": "data-standards"}),
        )
        selected = page.locator(".datagovuk-section-navigation__item--selected")
        expect(selected.get_by_role("link", name="Data standards", exact=True)).to_be_visible()

    def test_side_nav_selected_on_mobile(self, mobile_page, live_server_url):
        mobile_page.goto(
            live_server_url + reverse("data_manual:data_manual_page", kwargs={"data_manual_name": "data-standards"}),
        )
        pages_button = mobile_page.locator(".datagovuk-section-navigation__button")
        pages_button.click()
        selected = mobile_page.locator(".datagovuk-section-navigation__item--selected")
        expect(selected.get_by_role("link", name="Data standards", exact=True)).to_be_visible()

    def test_markdown_content(self, page, live_server_url):
        page.goto(
            live_server_url + reverse("data_manual:data_manual_page", kwargs={"data_manual_name": "data-standards"}),
        )
        content = page.locator(".datagovuk-main")
        expect(content.get_by_role("heading", name="Data standards", exact=True)).to_be_visible()
        expect(content.get_by_role("link", name="Open standards for government data and technology")).to_have_attribute(
            "href",
            "https://www.gov.uk/government/collections/open-standards-for-government-data-and-technology",
        )
        # Click a side nav link
        data_sharing_link = page.locator(".datagovuk-section-navigation__item").get_by_role(
            "link",
            name="Data sharing",
            exact=True,
        )
        data_sharing_link.click()
        expect(page).to_have_url(
            live_server_url + reverse("data_manual:data_manual_page", kwargs={"data_manual_name": "data-sharing"}),
        )
        expect(page.locator(".datagovuk-main").get_by_role("heading", name="Data sharing", exact=True)).to_be_visible()
        expect(
            page.locator(".datagovuk-main").get_by_role("link", name="Data sharing governance framework"),
        ).to_have_attribute(
            "href",
            "https://www.gov.uk/government/publications/data-sharing-governance-framework/data-sharing-governance-framework",
        )

    def test_markdown_content_on_mobile(self, mobile_page, live_server_url):
        mobile_page.goto(
            live_server_url + reverse("data_manual:data_manual_page", kwargs={"data_manual_name": "data-standards"}),
        )
        content = mobile_page.locator(".datagovuk-main")
        expect(content.get_by_role("heading", name="Data standards", exact=True)).to_be_visible()
        expect(content.get_by_role("link", name="Open standards for government data and technology")).to_have_attribute(
            "href",
            "https://www.gov.uk/government/collections/open-standards-for-government-data-and-technology",
        )
        # Click a data-manual pages nav link
        pages_button = mobile_page.locator(".datagovuk-section-navigation__button")
        pages_button.click()
        data_sharing_link = mobile_page.locator(".datagovuk-section-navigation__item").get_by_role(
            "link",
            name="Data sharing",
            exact=True,
        )
        data_sharing_link.click()
        expect(mobile_page).to_have_url(
            live_server_url + reverse("data_manual:data_manual_page", kwargs={"data_manual_name": "data-sharing"}),
        )
        expect(
            mobile_page.locator(".datagovuk-main").get_by_role("heading", name="Data sharing", exact=True),
        ).to_be_visible()
        expect(
            mobile_page.locator(".datagovuk-main").get_by_role("link", name="Data sharing governance framework"),
        ).to_have_attribute(
            "href",
            "https://www.gov.uk/government/publications/data-sharing-governance-framework/data-sharing-governance-framework",
        )
