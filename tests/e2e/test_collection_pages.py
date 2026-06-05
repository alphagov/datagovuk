import pytest
from django.urls import reverse
from playwright.sync_api import expect
from pytest_lazy_fixtures import lf

from datagovuk.collections.constants import get_collections_by_slug


@pytest.mark.smoke
def test_collection_pages(page, live_server_url):
    for collection_slug, collection_pages in get_collections_by_slug().items():
        for collection_page in collection_pages["topics"]:
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


def test_collection_page_has_cache_control_header_set(page, live_server_url):
    url = reverse(
        "collections:collection_page",
        kwargs={"collection_name": "land-and-property", "collection_page_name": "uk-house-prices"},
    )
    response = page.goto(live_server_url + url)
    cache_control = response.headers.get("cache-control")
    assert cache_control == "max-age=1800, public"


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
def test_collection_page_headline_is_visible(lazy_page, live_server_url):
    url = reverse(
        "collections:collection_page",
        kwargs={"collection_name": "transport", "collection_page_name": "road-traffic"},
    )
    lazy_page.goto(live_server_url + url)

    expect(lazy_page.get_by_role("heading", name="Cars and taxis")).to_be_visible()
    expect(lazy_page.get_by_role("heading", name="Buses and coaches")).to_be_visible()
    expect(lazy_page.get_by_text("Increase of 1.9% from 2023 to")).to_be_visible()
    expect(lazy_page.get_by_text("Increase of 1.7% from 2023 to")).to_be_visible()
    headline_column = lazy_page.locator(".datagovuk-headline__column").first
    expect(headline_column.locator(".datagovuk-headline__number", has_text="256.1")).to_be_visible()
    expect(headline_column.locator(".datagovuk-headline__change-value-percent", has_text="1.9%")).to_be_visible()


@pytest.mark.parametrize(
    "lazy_page",
    [
        lf("page"),
        lf("mobile_page"),
    ],
)
def test_collection_page_headline_no_percent_change(lazy_page, live_server_url, enable_early_years):
    url = reverse(
        "collections:collection_page",
        kwargs={"collection_name": "early-years", "collection_page_name": "education-statistics"},
    )
    lazy_page.goto(live_server_url + url)

    expect(lazy_page.get_by_role("heading", name="Good level of development")).to_be_visible()
    expect(lazy_page.get_by_role("heading", name="Expected level across all early learning goals")).to_be_visible()
    expect(lazy_page.get_by_text("In 2024/25, up from 65.2% in 2021/22.")).to_be_visible()
    expect(lazy_page.get_by_text("In 2024/25, up from 63.4% in 2021/22.")).to_be_visible()
    headline_column = lazy_page.locator(".datagovuk-headline__column").first
    expect(headline_column.locator(".datagovuk-headline__number", has_text="68.3%")).to_be_visible()
    expect(
        headline_column.locator(".datagovuk-headline__change-value", has_text="3.1 percentage points"),
    ).to_be_visible()
    expect(headline_column.locator(".datagovuk-headline__change-value-percent", has_text="(%)")).not_to_be_visible()


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


@pytest.mark.parametrize(
    "lazy_page",
    [
        lf("page"),
        lf("mobile_page"),
    ],
)
def test_collection_page_download(lazy_page, live_server_url):
    url = reverse(
        "collections:collection_page",
        kwargs={"collection_name": "business-and-economy", "collection_page_name": "uk-trade"},
    )
    lazy_page.goto(live_server_url + url)
    with lazy_page.expect_download() as download_info:
        lazy_page.get_by_role("link", name="Download the chart data").click()
    download = download_info.value
    assert download.suggested_filename == "total-uk-imports-exports.csv"


def test_collection_page_with_aria_current_page(page, live_server_url):
    url = reverse(
        "collections:collection_page",
        kwargs={"collection_name": "land-and-property", "collection_page_name": "uk-house-prices"},
    )
    page.goto(live_server_url + url)
    expect(page.get_by_role("link", name="UK house prices", exact=True)).to_have_attribute(
        "aria-current",
        "page",
    )


def test_collection_page_with_aria_current_mobile(mobile_page, live_server_url):
    url = reverse(
        "collections:collection_page",
        kwargs={"collection_name": "land-and-property", "collection_page_name": "uk-house-prices"},
    )
    mobile_page.goto(live_server_url + url)
    mobile_page.get_by_role("button", name="Pages").click()
    expect(mobile_page.get_by_role("link", name="UK house prices", exact=True)).to_have_attribute(
        "aria-current",
        "page",
    )
