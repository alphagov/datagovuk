import pytest
from django.urls import reverse
from playwright.sync_api import expect

from datagovuk.directory.e2e_fixtures import DATASET_SLUG, DATASET_UUID


@pytest.fixture
def dataset_url():
    return reverse("directory:dataset", kwargs={"uuid": DATASET_UUID, "slug": DATASET_SLUG})


class TestSupportingDocumentsTemplate:
    @pytest.mark.smoke
    def test_supporting_documents_table_has_correct_headers(
        self,
        page,
        live_server_url,
        dataset_url,
    ):
        page.goto(live_server_url + dataset_url)
        supporting_table = page.locator(".supporting-documents .datagovuk-table-container")
        headers = supporting_table.locator("thead th")
        expect(headers.nth(0)).to_have_text("Link")
        expect(headers.nth(1)).to_have_text("Format")
        expect(headers.nth(2)).to_have_text("Last updated")

    def test_supporting_document_links_have_correct_hrefs(
        self,
        page,
        live_server_url,
        dataset_url,
    ):
        page.goto(live_server_url + dataset_url)
        supporting_table = page.locator(".supporting-documents .datagovuk-table-container")
        expect(supporting_table.locator(".datagovuk-link", has_text="Annual Report 2023")).to_have_attribute(
            "href",
            "https://example.com/annual-report-2023.pdf",
        )
        expect(supporting_table.locator(".datagovuk-link", has_text="Methodology Notes")).to_have_attribute(
            "href",
            "https://example.com/methodology.docx",
        )

    def test_supporting_document_formats_are_shown(
        self,
        page,
        live_server_url,
        dataset_url,
    ):
        page.goto(live_server_url + dataset_url)
        supporting_table = page.locator(".supporting-documents .datagovuk-table-container")
        rows = supporting_table.locator("tbody tr.govuk-table__row")
        expect(rows.first.locator("td").nth(1)).to_contain_text("PDF")

    def test_supporting_document_dates_are_shown(
        self,
        page,
        live_server_url,
        dataset_url,
    ):
        page.goto(live_server_url + dataset_url)
        supporting_table = page.locator(".supporting-documents .datagovuk-table-container")
        expect(supporting_table.get_by_text("15/1/2024")).to_be_visible()
        expect(supporting_table.get_by_text("1/11/2023")).to_be_visible()
