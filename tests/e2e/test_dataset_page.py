from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from django.urls import reverse
from playwright.sync_api import expect

from datagovuk.directory.solr import SolrDatafile, SolrDataset

DATASET_UUID = "e3c7ffd4-4187-46fd-a590-99e2af539058"
DATASET_SLUG = "household-waste-recycling-centres"


@pytest.fixture(autouse=True)
def enable_solr_feature_flag(settings):
    settings.FEATURE_FLAGS_ENABLED = ["solr-search"]


@pytest.fixture
def dataset_url():
    return reverse("directory:dataset", kwargs={"uuid": DATASET_UUID, "slug": DATASET_SLUG})


@pytest.fixture
def mock_dataset():
    return SolrDataset(
        uuid=DATASET_UUID,
        name=DATASET_SLUG,
        title="Household Waste Recycling Centres",
        summary="A dataset about household waste recycling centres.",
        public_updated_at=datetime(2026, 1, 15, 10, 0, 0, tzinfo=UTC),
        topic="Environment",
        licence_title="Open Government Licence",
        licence_url="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        raw_doc={},
        organisation={"title": "Example Council", "name": "example-council"},
        datafiles=[
            SolrDatafile(
                name="Recycling Centre Locations",
                url="https://example.com/data.csv",
                created_at="2026-01-01",
                format="CSV",
                uuid="aaaaaaaa-0000-0000-0000-000000000001",
                last_modified=datetime(2026, 1, 10, 0, 0, 0, tzinfo=UTC),
                size="1024",
                is_csv=True,
            ),
        ],
    )


@pytest.fixture(autouse=True)
def mock_get_document(mock_dataset):
    with patch("datagovuk.directory.views.get_document", return_value=mock_dataset):
        yield


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
