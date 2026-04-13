from django.urls import reverse
from playwright.sync_api import expect


class TestDataManualHomePage:
    DATA_MANUAL_PAGES = {
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

    def test_data_manual_homepage_heading(self, page, live_server_url):
        page.goto(live_server_url + reverse("data_manual:home"))
        content = page.locator(".datagovuk-main")
        expect(content.get_by_role("heading", level=1)).to_have_text(
            "Data manual",
        )

    def test_data_manual_homepage_links(self, page, live_server_url):
        page.goto(live_server_url + reverse("data_manual:home"))
        for name, href in self.DATA_MANUAL_PAGES.items():
            link = page.get_by_role("link", name=name, exact=True)
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

    def test_join_our_community_link(self, page, live_server_url):
        page.goto(live_server_url + reverse("data_manual:home"))
        join_community_link = page.get_by_role("link", name="Join a data community")
        expect(join_community_link).to_have_attribute(
            "href",
            "/data-manual/join-a-data-community",
        )
