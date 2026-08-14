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
