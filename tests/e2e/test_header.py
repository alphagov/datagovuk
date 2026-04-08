from playwright.sync_api import expect


class TestHeader:
    def test_header(self, page, live_server_url) -> None:
        page.goto(live_server_url)
        expect(page.get_by_role("link", name="Home")).to_be_visible()
        expect(page.get_by_role("button", name="Collections")).to_be_visible()
        expect(page.get_by_role("button", name="Data manual")).to_be_visible()
        expect(page.get_by_role("banner").get_by_role("link", name="Directory")).to_be_visible()
        # Expect collection link to only be visible after clicking Collections sub-menu
        expect(
            page.locator("#datagovuk-menu-collections").get_by_role("link", name="Business and economy"),
        ).not_to_be_visible()
        page.get_by_role("button", name="Collections").click()
        expect(
            page.locator("#datagovuk-menu-collections").get_by_role("link", name="Business and economy"),
        ).to_be_visible()
        expect(page.locator("#datagovuk-menu-collections").get_by_role("link", name="Environment")).to_be_visible()
        expect(page.locator("#datagovuk-menu-collections").get_by_role("link", name="Government")).to_be_visible()
        expect(
            page.locator("#datagovuk-menu-collections").get_by_role("link", name="Land and property"),
        ).to_be_visible()
        expect(page.locator("#datagovuk-menu-collections").get_by_role("link", name="People")).to_be_visible()
        expect(page.locator("#datagovuk-menu-collections").get_by_role("link", name="Transport")).to_be_visible()
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

    def test_header_mobile(self, mobile_page, live_server_url) -> None:
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
