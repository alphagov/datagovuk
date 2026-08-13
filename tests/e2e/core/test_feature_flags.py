from playwright.sync_api import expect


def test_feature_flag_feature_flag_enabled(page, live_server_url, settings):
    settings.FEATURE_FLAGS_ENABLED = ["test-feature-flag"]
    page.goto(live_server_url)
    expect(page.locator("body")).to_contain_text("Test feature flag enabled")


def test_feature_flag_feature_flag_disabled(page, live_server_url):
    page.goto(live_server_url)
    expect(page.locator("body")).not_to_contain_text("Test feature flag enabled")
