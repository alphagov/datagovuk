import pytest
from django.urls import reverse
from playwright.sync_api import expect
from pytest_lazy_fixtures import lf


@pytest.fixture
def search_url():
    return reverse("directory:search")


class TestSearch:
    @pytest.mark.parametrize(
        "lazy_page",
        [
            lf("page"),
            lf("mobile_page"),
        ],
    )
    def test_search_query_only(
        self,
        lazy_page,
        live_server_url,
        search_url,
    ):
        lazy_page.goto(live_server_url + search_url)
        expect(lazy_page.get_by_role("heading", level=1, name="Directory")).to_be_visible()
        lazy_page.get_by_role("textbox", name="Search directory").click()
        lazy_page.get_by_role("textbox", name="Search directory").fill('"E2E Search"')
        lazy_page.get_by_role("button", name="Search").click()
        expect(lazy_page.get_by_text("1 to 6 of 6 results")).to_be_visible()
        expect(lazy_page.get_by_role("link", name="DGUK E2E Search dataset licence")).to_be_visible()
        expect(lazy_page.get_by_role("link", name="DGUK E2E Search dataset publisher")).to_be_visible()
        expect(lazy_page.get_by_role("link", name="DGUK E2E Search dataset generic")).to_be_visible()
        expect(lazy_page.get_by_role("link", name="DGUK E2E Search dataset format")).to_be_visible()
        expect(lazy_page.get_by_role("link", name="DGUK E2E Search dataset topic")).to_be_visible()
        expect(lazy_page.get_by_role("link", name="DGUK E2E Search dataset recent")).to_be_visible()

    @pytest.mark.parametrize(
        "lazy_page",
        [
            lf("page"),
            lf("mobile_page"),
        ],
    )
    def test_search_and_sort(
        self,
        lazy_page,
        live_server_url,
        search_url,
    ):
        lazy_page.goto(live_server_url + search_url)
        expect(lazy_page.get_by_role("heading", level=1, name="Directory")).to_be_visible()
        lazy_page.get_by_role("textbox", name="Search directory").click()
        lazy_page.get_by_role("textbox", name="Search directory").fill('"E2E Search"')
        lazy_page.get_by_role("button", name="Search").click()
        expect(lazy_page.get_by_text("1 to 6 of 6 results")).to_be_visible()
        lazy_page.get_by_label("Sort by").select_option("recent")
        results = lazy_page.locator(".datagovuk-search-results__item")
        expect(results.nth(0).get_by_role("link", name="DGUK E2E Search dataset recent")).to_be_visible()

    @pytest.mark.parametrize(
        "lazy_page",
        [
            lf("page"),
            lf("mobile_page"),
        ],
    )
    def test_search_filter_by_publisher(
        self,
        lazy_page,
        live_server_url,
        search_url,
    ):
        lazy_page.goto(live_server_url + search_url)
        expect(lazy_page.get_by_role("heading", level=1, name="Directory")).to_be_visible()
        lazy_page.get_by_role("textbox", name="Search directory").click()
        lazy_page.get_by_role("textbox", name="Search directory").fill('"E2E Search"')
        lazy_page.get_by_role("button", name="Search").click()
        lazy_page.get_by_role("combobox", name="Publisher").click()
        lazy_page.get_by_role("option", name="E2e publisher 2").click()
        lazy_page.get_by_role("button", name="Apply filters").click()
        expect(lazy_page.get_by_text("1 to 1 of 1 results")).to_be_visible()
        expect(lazy_page.get_by_role("link", name="DGUK E2E Search dataset publisher")).to_be_visible()

    @pytest.mark.parametrize(
        "lazy_page",
        [
            lf("page"),
            lf("mobile_page"),
        ],
    )
    def test_search_filter_by_topic(
        self,
        lazy_page,
        live_server_url,
        search_url,
    ):
        lazy_page.goto(live_server_url + search_url)
        expect(lazy_page.get_by_role("heading", level=1, name="Directory")).to_be_visible()
        lazy_page.get_by_role("textbox", name="Search directory").click()
        lazy_page.get_by_role("textbox", name="Search directory").fill('"E2E Search"')
        lazy_page.get_by_role("button", name="Search").click()
        lazy_page.get_by_role("combobox", name="Topic").click()
        lazy_page.get_by_role("option", name="Environment").click()
        lazy_page.get_by_role("button", name="Apply filters").click()
        expect(lazy_page.get_by_text("1 to 1 of 1 results")).to_be_visible()
        expect(lazy_page.get_by_role("link", name="DGUK E2E Search dataset topic")).to_be_visible()

    @pytest.mark.parametrize(
        "lazy_page",
        [
            lf("page"),
            lf("mobile_page"),
        ],
    )
    def test_search_filter_by_format(
        self,
        lazy_page,
        live_server_url,
        search_url,
    ):
        lazy_page.goto(live_server_url + search_url)
        expect(lazy_page.get_by_role("heading", level=1, name="Directory")).to_be_visible()
        lazy_page.get_by_role("textbox", name="Search directory").click()
        lazy_page.get_by_role("textbox", name="Search directory").fill('"E2E Search"')
        lazy_page.get_by_role("button", name="Search").click()
        lazy_page.get_by_role("combobox", name="Format").click()
        lazy_page.get_by_role("option", name="CSV").click()
        lazy_page.get_by_role("button", name="Apply filters").click()
        expect(lazy_page.get_by_text("1 to 1 of 1 results")).to_be_visible()
        expect(lazy_page.get_by_role("link", name="DGUK E2E Search dataset format")).to_be_visible()

    @pytest.mark.parametrize(
        "lazy_page",
        [
            lf("page"),
            lf("mobile_page"),
        ],
    )
    def test_search_filter_by_licence(
        self,
        lazy_page,
        live_server_url,
        search_url,
    ):
        lazy_page.goto(live_server_url + search_url)
        expect(lazy_page.get_by_role("heading", level=1, name="Directory")).to_be_visible()
        lazy_page.get_by_role("textbox", name="Search directory").click()
        lazy_page.get_by_role("textbox", name="Search directory").fill('"E2E Search"')
        lazy_page.get_by_role("button", name="Search").click()
        lazy_page.get_by_role("checkbox", name="Open Government Licence (OGL").check()
        lazy_page.get_by_role("button", name="Apply filters").click()
        expect(lazy_page.get_by_text("1 to 1 of 1 results")).to_be_visible()
        expect(lazy_page.get_by_role("link", name="DGUK E2E Search dataset licence")).to_be_visible()
