import pytest
from django.urls import reverse
from playwright.sync_api import expect
from pytest_lazy_fixtures import lf

from datagovuk.collections.constants import COLLECTIONS


def test_collection_pages(page, live_server_url):
    for collection_slug, collection_pages in COLLECTIONS.items():
        for collection_page in collection_pages:
            collection_path = reverse(
                "collections:collection_page",
                kwargs={
                    "collection_name": collection_slug,
                    "collection_page_name": collection_page["slug"],
                },
            )
            page.goto(
                live_server_url + collection_path,
            )
            main_content = page.locator(".datagovuk-main")
            expect(main_content.get_by_role("heading", level=1)).to_have_text(
                collection_page["title"],
            )
            expect(main_content.locator(".datagovuk-section-navigation__item--selected:visible")).to_have_text(
                collection_page["title"],
            )


@pytest.mark.parametrize(
    "lazy_page",
    [
        lf("page"),
        lf("mobile_page"),
    ],
)
def test_collection_page_line_chart_is_visible(lazy_page, live_server_url):
    url = reverse(
        "collections:collection_page",
        kwargs={"collection_name": "land-and-property", "collection_page_name": "uk-house-prices"},
    )
    lazy_page.goto(live_server_url + url)

    expect(lazy_page.locator(".line-chart")).to_be_visible()
    expect(lazy_page.locator(".line-chart canvas")).to_be_visible()
    expect(lazy_page.get_by_role("heading", level=2, name="Average house price")).to_be_visible()


@pytest.mark.parametrize(
    "lazy_page",
    [
        lf("page"),
        lf("mobile_page"),
    ],
)
def test_collection_page_bar_chart_is_visible(lazy_page, live_server_url):
    url = reverse(
        "collections:collection_page",
        kwargs={"collection_name": "government", "collection_page_name": "election-results"},
    )
    lazy_page.goto(live_server_url + url)

    expect(lazy_page.locator(".bar-chart")).to_be_visible()
    expect(lazy_page.locator(".bar-chart canvas")).to_be_visible()
    expect(lazy_page.get_by_role("heading", level=2, name="2024 Vote share by party (%)")).to_be_visible()


@pytest.mark.parametrize(
    "lazy_page",
    [
        lf("page"),
        lf("mobile_page"),
    ],
)
def test_collection_page_without_chart_has_no_chart(lazy_page, live_server_url):
    url = reverse(
        "collections:collection_page",
        kwargs={"collection_name": "land-and-property", "collection_page_name": "fire-statistics"},
    )
    lazy_page.goto(live_server_url + url)

    expect(lazy_page.locator(".line-chart")).to_have_count(0)
