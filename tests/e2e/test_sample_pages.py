from playwright.sync_api import expect


class TestPages:
    def test_homepage(self, page, live_server_url):
        page.goto(live_server_url)

        expect(page.get_by_role("heading", level=1)).to_have_text("data.gov.uk: Home")

    def test_about_page(self, page, live_server_url):
        page.goto(live_server_url + "/about/")

        expect(page.get_by_role("heading", level=1)).to_have_text("About data.gov.uk")
