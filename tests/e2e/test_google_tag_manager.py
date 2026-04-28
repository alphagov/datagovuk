import re


class TestGoogleTagManager:
    def test_google_tag_manager_is_present(self, page, live_server_url):
        regex = re.compile(
            r"https://www\.googletagmanager\.com/gtm\.js\?id=UA-XXXXX-Y&gtm_auth=fake-auth-token&gtm_preview=fake-preview-token&gtm_cookies_win=x",
        )

        with page.expect_request(regex):
            page.goto(live_server_url)
