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
        expect(page.get_by_role("heading", level=1, name="Search results")).to_be_visible()
        page.get_by_role("searchbox", name="Search directory").click()
        page.get_by_role("searchbox", name="Search directory").fill('"E2E Search"')
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
        expect(page.get_by_role("heading", level=1, name="Search results")).to_be_visible()
        page.get_by_role("searchbox", name="Search directory").click()
        page.get_by_role("searchbox", name="Search directory").fill('"E2E Search"')
        page.get_by_role("button", name="Search").click()
        expect(page.get_by_text("6 results")).to_be_visible()
        page.get_by_role("button", name="Sort by").click()
        page.get_by_role("option", name="Most Recent").click()
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
        expect(page.get_by_role("heading", level=1, name="Search results")).to_be_visible()
        page.get_by_role("searchbox", name="Search directory").click()
        page.get_by_role("searchbox", name="Search directory").fill('"E2E Search"')
        page.get_by_role("button", name="Search").click()
        # Wait for autocomplete JS to catch up..
        page.wait_for_timeout(1000)
        page.get_by_role("checkbox", name="E2e publisher 2").check()
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
        expect(page.get_by_role("heading", level=1, name="Search results")).to_be_visible()
        page.get_by_role("searchbox", name="Search directory").click()
        page.get_by_role("searchbox", name="Search directory").fill('"E2E Search"')
        page.get_by_role("button", name="Search").click()
        # Wait for autocomplete JS to catch up..
        page.wait_for_timeout(1000)
        page.get_by_role("checkbox", name="Environment").check()
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
        expect(page.get_by_role("heading", level=1, name="Search results")).to_be_visible()
        page.get_by_role("searchbox", name="Search directory").click()
        page.get_by_role("searchbox", name="Search directory").fill('"E2E Search"')
        page.get_by_role("button", name="Search").click()
        # Wait for autocomplete JS to catch up..
        page.wait_for_timeout(1000)
        page.get_by_role("checkbox", name="CSV").check()
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
        expect(page.get_by_role("heading", level=1, name="Search results")).to_be_visible()
        page.get_by_role("searchbox", name="Search directory").click()
        page.get_by_role("searchbox", name="Search directory").fill('"E2E Search"')
        page.get_by_role("button", name="Search").click()
        # Wait for autocomplete JS to catch up..
        page.wait_for_timeout(1000)
        page.get_by_role("checkbox", name="Open Government Licence (OGL").check()
        expect(page.get_by_text("1 result")).to_be_visible()
        expect(page.get_by_role("link", name="DGUK E2E Search dataset licence")).to_be_visible()

    @pytest.mark.smoke
    def test_search_show_missing_links(
        self,
        page,
        live_server_url,
        search_url,
    ):
        page.goto(live_server_url + search_url)
        expect(page.get_by_role("heading", level=1, name="Search results")).to_be_visible()
        page.get_by_role("searchbox", name="Search directory").click()
        page.get_by_role("searchbox", name="Search directory").fill('"E2E Search"')
        page.get_by_role("button", name="Search").click()
        # Wait for autocomplete JS to catch up..
        page.wait_for_timeout(1000)
        page.get_by_role("checkbox", name="Include datasets with no links").check()
        expect(page.get_by_text("7 results")).to_be_visible()
        expect(page.get_by_role("link", name="DGUK E2E Search dataset licence")).to_be_visible()
        expect(page.get_by_role("link", name="DGUK E2E Search dataset publisher")).to_be_visible()
        expect(page.get_by_role("link", name="DGUK E2E Search dataset generic")).to_be_visible()
        expect(page.get_by_role("link", name="DGUK E2E Search dataset format")).to_be_visible()
        expect(page.get_by_role("link", name="DGUK E2E Search dataset topic")).to_be_visible()
        expect(page.get_by_role("link", name="DGUK E2E Search dataset missing links")).to_be_visible()
        expect(page.get_by_role("link", name="DGUK E2E Search dataset recent")).to_be_visible()
