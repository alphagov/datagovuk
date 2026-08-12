from playwright.sync_api import expect


def test_directory_header_publish_your_data_links_to_publishers_page(page, live_server_url):
    page.goto(live_server_url + "/search")
    expect(page.locator(".datagovuk-directory-header__link", has_text="Publish your data")).to_have_attribute(
        "href",
        "/publishers/",
    )


def test_directory_header_publish_your_data_mobile_menu_links_to_publishers_page(mobile_page, live_server_url):
    mobile_page.goto(live_server_url + "/search")
    mobile_page.locator("#datagovuk-directory-header-button-all").click()
    expect(
        mobile_page.locator(".datagovuk-directory-menu .datagovuk-menu__item-link", has_text="Publish your data"),
    ).to_have_attribute("href", "/publishers/")
