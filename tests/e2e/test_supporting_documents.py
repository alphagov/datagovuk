import uuid

import pysolr
import pytest
from django.urls import reverse
from playwright.sync_api import expect

from datagovuk.directory.tests.conftest import (
    SolrDocumentFactory,
    SolrOrganisationFactory,
    make_supporting_document,
    make_validated_data_dict,
)

DATASET_UUID = str(uuid.uuid4())
DATASET_SLUG = "test-supporting-documents-dataset"


@pytest.fixture(autouse=True)
def enable_solr_feature_flag(settings):
    settings.FEATURE_FLAGS_ENABLED = ["solr-search"]


@pytest.fixture
def solr(settings):
    client = pysolr.Solr(settings.SOLR_URL, always_commit=True)
    yield client
    client.delete(q=f"id:{DATASET_UUID}")


@pytest.fixture
def dataset_with_supporting_docs(solr):
    resources = [
        make_supporting_document(
            id=str(uuid.uuid4()),
            name="Annual Report 2023",
            url="https://example.com/annual-report-2023.pdf",
            format="PDF",
            last_modified="2024-01-15T00:00:00+00:00",
        ),
        make_supporting_document(
            id=str(uuid.uuid4()),
            name="Methodology Notes",
            url="https://example.com/methodology.docx",
            format="DOCX",
            last_modified="2023-11-01T00:00:00+00:00",
        ),
    ]
    doc = SolrDocumentFactory(
        id=DATASET_UUID,
        name=DATASET_SLUG,
        title="Test Supporting Documents Dataset",
        validated_data_dict=make_validated_data_dict(resources=resources),
    )
    organisation_doc = SolrOrganisationFactory(
        title="Example Publisher 1",
        name=doc["organization"],
    )
    solr.add([doc, organisation_doc])
    return doc


@pytest.fixture
def dataset_url():
    return reverse("directory:dataset", kwargs={"uuid": DATASET_UUID, "slug": DATASET_SLUG})


class TestSupportingDocumentsTemplate:
    def test_supporting_documents_table_has_correct_headers(
        self,
        page,
        live_server_url,
        dataset_url,
        dataset_with_supporting_docs,
    ):
        page.goto(live_server_url + dataset_url)
        supporting_table = page.locator(".support-documents .datagovuk-table-container")
        headers = supporting_table.locator("thead th")
        expect(headers.nth(0)).to_have_text("Link")
        expect(headers.nth(1)).to_have_text("Format")
        expect(headers.nth(2)).to_have_text("Last updated")

    def test_supporting_document_links_have_correct_hrefs(
        self,
        page,
        live_server_url,
        dataset_url,
        dataset_with_supporting_docs,
    ):
        page.goto(live_server_url + dataset_url)
        supporting_table = page.locator(".support-documents .datagovuk-table-container")
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
        dataset_with_supporting_docs,
    ):
        page.goto(live_server_url + dataset_url)
        supporting_table = page.locator(".support-documents .datagovuk-table-container")
        rows = supporting_table.locator("tbody tr.govuk-table__row")
        expect(rows.first.locator("td").nth(1)).to_contain_text("PDF")

    def test_supporting_document_dates_are_shown(
        self,
        page,
        live_server_url,
        dataset_url,
        dataset_with_supporting_docs,
    ):
        page.goto(live_server_url + dataset_url)
        supporting_table = page.locator(".support-documents .datagovuk-table-container")
        expect(supporting_table.get_by_text("15/01/2024")).to_be_visible()
        expect(supporting_table.get_by_text("01/11/2023")).to_be_visible()
