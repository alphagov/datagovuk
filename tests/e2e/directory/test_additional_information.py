import pytest
from django.urls import reverse
from playwright.sync_api import expect

from datagovuk.directory.e2e_fixtures import DATASET_SLUG, DATASET_UUID, DATASET_UUID_NO_EXTRAS


@pytest.fixture
def dataset_url():
    return reverse("directory:dataset", kwargs={"uuid": DATASET_UUID, "slug": DATASET_SLUG})


@pytest.fixture
def dataset_url_no_extras():
    return reverse("directory:dataset", kwargs={"uuid": DATASET_UUID_NO_EXTRAS, "slug": DATASET_SLUG})


class TestAdditionalInformationSection:
    def test_additional_information_heading_is_visible(
        self,
        page,
        live_server_url,
        dataset_url,
    ):
        page.goto(live_server_url + dataset_url)
        expect(page.get_by_role("heading", level=2, name="Additional information")).to_be_visible()

    def test_additional_information_heading_absent_when_no_extras(
        self,
        page,
        live_server_url,
        dataset_url_no_extras,
    ):
        page.goto(live_server_url + dataset_url_no_extras)
        section = page.locator(".additional-information")
        expect(section.get_by_role("button", name="View additional information")).to_have_count(0)
        expect(page.get_by_role("heading", level=2, name="Additional information")).to_have_count(0)

    def test_additional_information_section_collapsed(
        self,
        page,
        live_server_url,
        dataset_url,
    ):
        page.goto(live_server_url + dataset_url)
        section = page.locator(".additional-information")
        expect(section.locator("#additional-information")).to_be_hidden()
        expect(page.get_by_role("heading", level=2, name="Additional information")).to_be_visible()
        expect(section.get_by_role("button", name="View additional information")).to_be_visible()

    def test_metadata_date_is_shown(
        self,
        page,
        live_server_url,
        dataset_url,
    ):
        page.goto(live_server_url + dataset_url)
        section = page.locator(".additional-information")
        section.get_by_role("button", name="View additional information").click()
        expect(section.get_by_text("Date added")).to_be_visible()
        expect(section.get_by_text("01 June 2024", exact=False).first).to_be_visible()

    def test_harvest_guid_is_shown(
        self,
        page,
        live_server_url,
        dataset_url,
    ):
        page.goto(live_server_url + dataset_url)
        section = page.locator(".additional-information")
        section.get_by_role("button", name="View additional information").click()
        expect(section.get_by_text("Harvest GUID")).to_be_visible()
        expect(section.get_by_text("a1b2c3d4-0000-0000-0000-000000000001", exact=False)).to_be_visible()

    def test_frequency_of_update_is_shown(
        self,
        page,
        live_server_url,
        dataset_url,
    ):
        page.goto(live_server_url + dataset_url)
        section = page.locator(".additional-information")
        section.get_by_role("button", name="View additional information").click()
        expect(section.get_by_text("Frequency of update")).to_be_visible()
        expect(section.get_by_text("annual", exact=False)).to_be_visible()

    def test_spatial_reference_system_is_shown(
        self,
        page,
        live_server_url,
        dataset_url,
    ):
        page.goto(live_server_url + dataset_url)
        section = page.locator(".additional-information")
        section.get_by_role("button", name="View additional information").click()
        expect(section.get_by_text("Spatial reference system")).to_be_visible()
        expect(section.get_by_text("OSGB 1936 / Test", exact=False)).to_be_visible()

    def test_extent_latitude_and_longitude_shown_as_separate_rows(
        self,
        page,
        live_server_url,
        dataset_url,
    ):
        page.goto(live_server_url + dataset_url)
        section = page.locator(".additional-information")
        section.get_by_role("button", name="View additional information").click()
        expect(section.get_by_text("Extent (Latitude)")).to_be_visible()
        expect(section.get_by_text("Extent (Longitude)")).to_be_visible()
        expect(section.get_by_text("51.686° to 51.286°", exact=False)).to_be_visible()
        expect(section.get_by_text("-0.510° to -0.489°", exact=False)).to_be_visible()

    def test_access_constraints_is_shown(
        self,
        page,
        live_server_url,
        dataset_url,
    ):
        page.goto(live_server_url + dataset_url)
        section = page.locator(".additional-information")
        section.get_by_role("button", name="View additional information").click()
        expect(section.get_by_text("Access constraints")).to_be_visible()
        expect(section.get_by_text("Available under the Open Government Licence v3.0", exact=False)).to_be_visible()

    def test_dataset_reference_date_is_shown_as_separate_rows(
        self,
        page,
        live_server_url,
        dataset_url,
    ):
        page.goto(live_server_url + dataset_url)
        section = page.locator(".additional-information")
        section.get_by_role("button", name="View additional information").click()
        expect(section.get_by_text("Dataset reference date (publication)")).to_be_visible()
        expect(section.get_by_text("Dataset reference date (revision)")).to_be_visible()
        expect(section.get_by_text("2024-01-01", exact=False).first).to_be_visible()
        expect(section.get_by_text("2024-06-01", exact=False).first).to_be_visible()

    def test_responsible_party_is_shown(
        self,
        page,
        live_server_url,
        dataset_url,
    ):
        page.goto(live_server_url + dataset_url)
        section = page.locator(".additional-information")
        section.get_by_role("button", name="View additional information").click()
        expect(section.get_by_text("Responsible party")).to_be_visible()
        expect(section.get_by_text("Example Publisher (pointOfContact)", exact=False)).to_be_visible()

    def test_metadata_language_is_shown(
        self,
        page,
        live_server_url,
        dataset_url,
    ):
        page.goto(live_server_url + dataset_url)
        section = page.locator(".additional-information")
        section.get_by_role("button", name="View additional information").click()
        expect(section.get_by_text("Metadata language")).to_be_visible()
        expect(section.get_by_text("eng", exact=False)).to_be_visible()

    def test_iso_resource_type_is_shown(
        self,
        page,
        live_server_url,
        dataset_url,
    ):
        page.goto(live_server_url + dataset_url)
        section = page.locator(".additional-information")
        section.get_by_role("button", name="View additional information").click()
        expect(section.get_by_text("ISO 19139 resource type")).to_be_visible()
        expect(section.locator("dd").get_by_text("dataset", exact=True)).to_be_visible()

    def test_source_metadata_links_are_shown(
        self,
        page,
        live_server_url,
        dataset_url,
    ):
        page.goto(live_server_url + dataset_url)
        section = page.locator(".additional-information")
        section.get_by_role("button", name="View additional information").click()
        expect(section.get_by_text("Source Metadata")).to_be_visible()
        expect(section.get_by_role("link", name="XML")).to_have_attribute(
            "href",
            "/api/2/rest/harvestobject/harvest-object-abc123/xml",
        )
        expect(section.get_by_role("link", name="HTML")).to_have_attribute(
            "href",
            "/api/2/rest/harvestobject/harvest-object-abc123/html",
        )
