from playwright.sync_api import expect


class TestSupportFormPage:
    def test_support_form_page_content(self, page, live_server_url, settings):
        page.goto(live_server_url + "/support/")

        expect(page.get_by_role("heading", level=1)).to_have_text("Contact National Data Library")
        expect(page.locator("label", has_text="What are the details")).to_have_count(1)
        expect(page.locator("text=You can enter up to 1200 characters")).to_have_count(1)
        expect(page.locator("label", has_text="Your name")).to_have_count(1)
        expect(page.locator("label", has_text="Your email address")).to_have_count(1)
        expect(page.get_by_role("link", name="Join the National Data Library on Slack")).to_have_attribute(
            "href",
            "https://ukgovernmentdigital.slack.com/archives/C037J3GTE4T",
        )

    def test_support_form_empty_submission_shows_validation_error(self, page, live_server_url, settings):
        page.goto(live_server_url + "/support/")

        page.get_by_role("button", name="Send message").click()

        expect(page.locator("text=This field is required.")).to_have_count(1)
