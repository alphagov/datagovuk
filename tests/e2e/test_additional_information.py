import json
import os
import uuid

import pysolr
import pytest
from django.urls import reverse
from playwright.sync_api import expect

from datagovuk.directory.tests.conftest import SolrDocumentFactory, make_validated_data_dict

DATASET_UUID = str(uuid.uuid4())
DATASET_UUID_NO_EXTRAS = str(uuid.uuid4())
DATASET_SLUG = "test-additional-information-dataset"
SOLR_URL = os.getenv("SOLR_URL", "http://localhost:8984/solr/ckan-test")


@pytest.fixture(autouse=True)
def enable_solr_feature_flag(settings):
    settings.FEATURE_FLAGS_ENABLED = ["solr-search"]
    settings.SOLR_URL = SOLR_URL


@pytest.fixture
def solr():
    client = pysolr.Solr(SOLR_URL, always_commit=True)
    yield client
    client.delete(q=f"id:{DATASET_UUID} OR id:{DATASET_UUID_NO_EXTRAS}")


@pytest.fixture
def dataset_url():
    return reverse("directory:dataset", kwargs={"uuid": DATASET_UUID, "slug": DATASET_SLUG})


@pytest.fixture
def dataset_with_additional_information(solr):
    extras = [
        {"key": "licence", "value": "ogl"},
        {"key": "metadata-date", "value": "2024-06-01T00:00:00"},
        {"key": "guid", "value": "a1b2c3d4-0000-0000-0000-000000000001"},
        {"key": "frequency-of-update", "value": "annual"},
        {"key": "metadata-language", "value": "eng"},
        {"key": "spatial-reference-system", "value": "OSGB 1936 / Test"},
        {"key": "responsible-party", "value": "Example Publisher (pointOfContact)"},
        {"key": "access_constraints", "value": '["Available under the Open Government Licence v3.0"]'},
        {
            "key": "dataset-reference-date",
            "value": json.dumps(
                [{"type": "publication", "value": "2024-01-01"}, {"type": "revision", "value": "2024-06-01"}],
            ),
        },
        {
            "key": "bbox-north-lat",
            "value": "51.686",
        },
        {
            "key": "bbox-south-lat",
            "value": "51.286",
        },
        {
            "key": "bbox-west-long",
            "value": "-0.510",
        },
        {
            "key": "bbox-east-long",
            "value": "-0.489",
        },
        {"key": "metadata-language", "value": "eng"},
        {"key": "resource-type", "value": "dataset"},
        {"key": "harvest_object_id", "value": "harvest-object-abc123"},
    ]
    doc = SolrDocumentFactory(
        id=DATASET_UUID,
        name=DATASET_SLUG,
        title="Test Additional Information Dataset",
        validated_data_dict=make_validated_data_dict(extras=extras),
    )
    solr.add([doc])
    return doc


@pytest.fixture
def dataset_without_additional_information(solr):
    doc = SolrDocumentFactory(
        id=DATASET_UUID_NO_EXTRAS,
        name=DATASET_SLUG,
        title="Test No Additional Information Dataset",
        validated_data_dict=make_validated_data_dict(),
    )
    solr.add([doc])
    return doc


@pytest.fixture
def dataset_url_no_extras():
    return reverse("directory:dataset", kwargs={"uuid": DATASET_UUID_NO_EXTRAS, "slug": DATASET_SLUG})


class TestAdditionalInformationSection:
    def test_additional_information_heading_is_visible(
        self,
        page,
        live_server_url,
        dataset_url,
        dataset_with_additional_information,
    ):
        page.goto(live_server_url + dataset_url)
        expect(page.get_by_role("heading", level=2, name="Additional information")).to_be_visible()

    def test_additional_information_heading_absent_when_no_extras(
        self,
        page,
        live_server_url,
        dataset_url_no_extras,
        dataset_without_additional_information,
    ):
        page.goto(live_server_url + dataset_url_no_extras)
        section = page.locator(".additional-information")
        expect(section.get_by_role("button", name="Show more")).to_have_count(0)
        expect(page.get_by_role("heading", level=2, name="Additional information")).to_have_count(0)

    def test_additional_information_section_collapsed(
        self,
        page,
        live_server_url,
        dataset_url,
        dataset_with_additional_information,
    ):
        page.goto(live_server_url + dataset_url)
        section = page.locator(".additional-information")
        expect(section.locator("#additional-information")).to_be_hidden()
        expect(page.get_by_role("heading", level=2, name="Additional information")).to_be_visible()
        expect(section.get_by_role("button", name="Show more")).to_be_visible()

    def test_metadata_date_is_shown(
        self,
        page,
        live_server_url,
        dataset_url,
        dataset_with_additional_information,
    ):
        page.goto(live_server_url + dataset_url)
        section = page.locator(".additional-information")
        section.get_by_role("button", name="Show more").click()
        expect(section.get_by_text("Date added")).to_be_visible()
        expect(section.get_by_text("01 June 2024", exact=False).first).to_be_visible()

    def test_harvest_guid_is_shown(
        self,
        page,
        live_server_url,
        dataset_url,
        dataset_with_additional_information,
    ):
        page.goto(live_server_url + dataset_url)
        section = page.locator(".additional-information")
        section.get_by_role("button", name="Show more").click()
        expect(section.get_by_text("Harvest GUID")).to_be_visible()
        expect(section.get_by_text("a1b2c3d4-0000-0000-0000-000000000001", exact=False)).to_be_visible()

    def test_frequency_of_update_is_shown(
        self,
        page,
        live_server_url,
        dataset_url,
        dataset_with_additional_information,
    ):
        page.goto(live_server_url + dataset_url)
        section = page.locator(".additional-information")
        section.get_by_role("button", name="Show more").click()
        expect(section.get_by_text("Frequency of update")).to_be_visible()
        expect(section.get_by_text("annual", exact=False)).to_be_visible()

    def test_spatial_reference_system_is_shown(
        self,
        page,
        live_server_url,
        dataset_url,
        dataset_with_additional_information,
    ):
        page.goto(live_server_url + dataset_url)
        section = page.locator(".additional-information")
        section.get_by_role("button", name="Show more").click()
        expect(section.get_by_text("Spatial reference system")).to_be_visible()
        expect(section.get_by_text("OSGB 1936 / Test", exact=False)).to_be_visible()

    def test_extent_latitude_and_longitude_shown_as_separate_rows(
        self,
        page,
        live_server_url,
        dataset_url,
        dataset_with_additional_information,
    ):
        page.goto(live_server_url + dataset_url)
        section = page.locator(".additional-information")
        section.get_by_role("button", name="Show more").click()
        expect(section.get_by_text("Extent (Latitude)")).to_be_visible()
        expect(section.get_by_text("Extent (Longitude)")).to_be_visible()
        expect(section.get_by_text("51.686° to 51.286°", exact=False)).to_be_visible()
        expect(section.get_by_text("-0.510° to -0.489°", exact=False)).to_be_visible()

    def test_access_constraints_is_shown(
        self,
        page,
        live_server_url,
        dataset_url,
        dataset_with_additional_information,
    ):
        page.goto(live_server_url + dataset_url)
        section = page.locator(".additional-information")
        section.get_by_role("button", name="Show more").click()
        expect(section.get_by_text("Access constraints")).to_be_visible()
        expect(section.get_by_text("Available under the Open Government Licence v3.0", exact=False)).to_be_visible()

    def test_dataset_reference_date_is_shown_as_separate_rows(
        self,
        page,
        live_server_url,
        dataset_url,
        dataset_with_additional_information,
    ):
        page.goto(live_server_url + dataset_url)
        section = page.locator(".additional-information")
        section.get_by_role("button", name="Show more").click()
        expect(section.get_by_text("Dataset reference date (publication)")).to_be_visible()
        expect(section.get_by_text("Dataset reference date (revision)")).to_be_visible()
        expect(section.get_by_text("2024-01-01", exact=False).first).to_be_visible()
        expect(section.get_by_text("2024-06-01", exact=False).first).to_be_visible()

    def test_responsible_party_is_shown(
        self,
        page,
        live_server_url,
        dataset_url,
        dataset_with_additional_information,
    ):
        page.goto(live_server_url + dataset_url)
        section = page.locator(".additional-information")
        section.get_by_role("button", name="Show more").click()
        expect(section.get_by_text("Responsible party")).to_be_visible()
        expect(section.get_by_text("Example Publisher (pointOfContact)", exact=False)).to_be_visible()

    def test_metadata_language_is_shown(
        self,
        page,
        live_server_url,
        dataset_url,
        dataset_with_additional_information,
    ):
        page.goto(live_server_url + dataset_url)
        section = page.locator(".additional-information")
        section.get_by_role("button", name="Show more").click()
        expect(section.get_by_text("Metadata language")).to_be_visible()
        expect(section.get_by_text("eng", exact=False)).to_be_visible()

    def test_iso_resource_type_is_shown(
        self,
        page,
        live_server_url,
        dataset_url,
        dataset_with_additional_information,
    ):
        page.goto(live_server_url + dataset_url)
        section = page.locator(".additional-information")
        section.get_by_role("button", name="Show more").click()
        expect(section.get_by_text("ISO 19139 resource type")).to_be_visible()
        expect(section.locator("dd").get_by_text("dataset", exact=True)).to_be_visible()

    def test_source_metadata_links_are_shown(
        self,
        page,
        live_server_url,
        dataset_url,
        dataset_with_additional_information,
    ):
        page.goto(live_server_url + dataset_url)
        section = page.locator(".additional-information")
        section.get_by_role("button", name="Show more").click()
        expect(section.get_by_text("Source Metadata")).to_be_visible()
        expect(section.get_by_role("link", name="XML")).to_have_attribute(
            "href",
            "/api/2/rest/harvestobject/harvest-object-abc123/xml",
        )
        expect(section.get_by_role("link", name="HTML")).to_have_attribute(
            "href",
            "/api/2/rest/harvestobject/harvest-object-abc123/html",
        )
