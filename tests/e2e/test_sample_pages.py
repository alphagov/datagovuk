from django.urls import reverse
from playwright.sync_api import expect


class TestPages:
    def test_about_page(self, page, live_server_url):
        page.goto(live_server_url + reverse("pages:about"))
        expect(page.get_by_role("heading", level=1)).to_have_text("About data.gov.uk")
