import re


class TestGoogleTagManager:
    def test_google_tag_manager_is_present(self, page, live_server_url, settings):
        settings.GOOGLE_TAG_MANAGER_ID = "UA-XXXXX-Y"
        settings.GOOGLE_TAG_MANAGER_AUTH = "fake-auth-token"
        settings.GOOGLE_TAG_MANAGER_PREVIEW = "fake-preview-token"

        regex = re.compile(
            r"https://www\.googletagmanager\.com/gtm\.js\?id=UA-XXXXX-Y&gtm_auth=fake-auth-token&gtm_preview=fake-preview-token&gtm_cookies_win=x",
        )

        with page.expect_request(regex):
            page.goto(live_server_url)
