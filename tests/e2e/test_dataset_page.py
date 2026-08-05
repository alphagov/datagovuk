import pytest
from django.urls import reverse
from playwright.sync_api import expect

DATASET_UUID = "e3c7ffd4-4187-46fd-a590-99e2af539058"
DATASET_SLUG = "household-waste-recycling-centres"


@pytest.fixture(autouse=True)
def enable_solr_feature_flag(settings):
    settings.FEATURE_FLAGS_ENABLED = ["solr-search"]


@pytest.fixture
def dataset_url():
    return reverse("directory:dataset", kwargs={"uuid": DATASET_UUID, "slug": DATASET_SLUG})


class TestDatasetPage:
    def test_heading_is_visible(self, page, live_server_url, dataset_url):
        page.goto(live_server_url + dataset_url)
        expect(page.get_by_role("heading", level=1)).to_have_text("Household Waste Recycling Centres")

    def test_data_links_heading_present(self, page, live_server_url, dataset_url):
        page.goto(live_server_url + dataset_url)
        expect(page.get_by_role("heading", level=2, name="Data links")).to_be_visible()

    def test_table_visible(self, page, live_server_url, dataset_url):
        page.goto(live_server_url + dataset_url)
        expect(page.locator(".datagovuk-table-container")).to_be_visible()

    def test_table_has_correct_column_headers(self, page, live_server_url, dataset_url):
        page.goto(live_server_url + dataset_url)
        headers = page.locator("thead.govuk-table__head tr th.govuk-table__header.datagovuk-table__header")
        expect(headers.nth(0)).to_have_text("Link")
        expect(headers.nth(1)).to_have_text("Format")
        expect(headers.nth(2)).to_have_text("Preview")
        expect(headers.nth(3)).to_have_text("Last updated")

    def test_table_rows_have_govuk_classes(self, page, live_server_url, dataset_url):
        page.goto(live_server_url + dataset_url)
        rows = page.locator("tbody tr.govuk-table__row")
        expect(rows.first.locator("td.govuk-table__cell.datagovuk-table__cell")).to_have_count(4)
