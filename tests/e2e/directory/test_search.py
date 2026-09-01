import pytest
from django.urls import reverse
from playwright.sync_api import expect


@pytest.fixture
def search_url():
    return reverse("directory:search")


class TestSearch:
    @pytest.mark.smoke
    def test_search_query_only(
        self,
        page,
        live_server_url,
        search_url,
    ):
        page.goto(live_server_url + search_url)
        expect(page.get_by_role("heading", level=1, name="Directory")).to_be_visible()
        page.get_by_role("textbox", name="Search directory").click()
        page.get_by_role("textbox", name="Search directory").fill('"E2E Search"')
        page.get_by_role("button", name="Search").click()
        expect(page.get_by_text("6 results")).to_be_visible()
        expect(page.get_by_role("link", name="DGUK E2E Search dataset licence")).to_be_visible()
        expect(page.get_by_role("link", name="DGUK E2E Search dataset publisher")).to_be_visible()
        expect(page.get_by_role("link", name="DGUK E2E Search dataset generic")).to_be_visible()
        expect(page.get_by_role("link", name="DGUK E2E Search dataset format")).to_be_visible()
        expect(page.get_by_role("link", name="DGUK E2E Search dataset topic")).to_be_visible()
        expect(page.get_by_role("link", name="DGUK E2E Search dataset recent")).to_be_visible()

    @pytest.mark.smoke
    def test_search_and_sort(
        self,
        page,
        live_server_url,
        search_url,
    ):
        page.goto(live_server_url + search_url)
        expect(page.get_by_role("heading", level=1, name="Directory")).to_be_visible()
        page.get_by_role("textbox", name="Search directory").click()
        page.get_by_role("textbox", name="Search directory").fill('"E2E Search"')
        page.get_by_role("button", name="Search").click()
        expect(page.get_by_text("6 results")).to_be_visible()
        page.get_by_label("Sort by").select_option("recent")
        results = page.locator(".datagovuk-search-results__item")
        expect(results.nth(0).get_by_role("link", name="DGUK E2E Search dataset recent")).to_be_visible()

    @pytest.mark.smoke
    def test_search_filter_by_publisher(
        self,
        page,
        live_server_url,
        search_url,
    ):
        page.goto(live_server_url + search_url)
        expect(page.get_by_role("heading", level=1, name="Directory")).to_be_visible()
        page.get_by_role("textbox", name="Search directory").click()
        page.get_by_role("textbox", name="Search directory").fill('"E2E Search"')
        page.get_by_role("button", name="Search").click()
        # Wait for autocomplete JS to catch up..
        page.wait_for_timeout(1000)
        page.get_by_role("combobox", name="Publisher").click()
        page.get_by_role("option", name="E2e publisher 2").click()
        page.get_by_role("button", name="Apply filters").click()
        expect(page.get_by_text("1 result")).to_be_visible()
        expect(page.get_by_role("link", name="DGUK E2E Search dataset publisher")).to_be_visible()

    @pytest.mark.smoke
    def test_search_filter_by_topic(
        self,
        page,
        live_server_url,
        search_url,
    ):
        page.goto(live_server_url + search_url)
        expect(page.get_by_role("heading", level=1, name="Directory")).to_be_visible()
        page.get_by_role("textbox", name="Search directory").click()
        page.get_by_role("textbox", name="Search directory").fill('"E2E Search"')
        page.get_by_role("button", name="Search").click()
        # Wait for autocomplete JS to catch up..
        page.wait_for_timeout(1000)
        page.get_by_role("combobox", name="Topic").click()
        page.get_by_role("option", name="Environment").click()
        page.get_by_role("button", name="Apply filters").click()
        expect(page.get_by_text("1 result")).to_be_visible()
        expect(page.get_by_role("link", name="DGUK E2E Search dataset topic")).to_be_visible()

    @pytest.mark.smoke
    def test_search_filter_by_format(
        self,
        page,
        live_server_url,
        search_url,
    ):
        page.goto(live_server_url + search_url)
        expect(page.get_by_role("heading", level=1, name="Directory")).to_be_visible()
        page.get_by_role("textbox", name="Search directory").click()
        page.get_by_role("textbox", name="Search directory").fill('"E2E Search"')
        page.get_by_role("button", name="Search").click()
        # Wait for autocomplete JS to catch up..
        page.wait_for_timeout(1000)
        page.get_by_role("combobox", name="Format").click()
        page.get_by_role("option", name="CSV").click()
        page.get_by_role("button", name="Apply filters").click()
        expect(page.get_by_text("1 result")).to_be_visible()
        expect(page.get_by_role("link", name="DGUK E2E Search dataset format")).to_be_visible()

    @pytest.mark.smoke
    def test_search_filter_by_licence(
        self,
        page,
        live_server_url,
        search_url,
    ):
        page.goto(live_server_url + search_url)
        expect(page.get_by_role("heading", level=1, name="Directory")).to_be_visible()
        page.get_by_role("textbox", name="Search directory").click()
        page.get_by_role("textbox", name="Search directory").fill('"E2E Search"')
        page.get_by_role("button", name="Search").click()
        # Wait for autocomplete JS to catch up..
        page.wait_for_timeout(1000)
        page.get_by_role("checkbox", name="Open Government Licence (OGL").check()
        page.get_by_role("button", name="Apply filters").click()
        expect(page.get_by_text("1 result")).to_be_visible()
        expect(page.get_by_role("link", name="DGUK E2E Search dataset licence")).to_be_visible()
