import pytest
from django.urls import reverse
from playwright.sync_api import expect

DATASET_UUID = "e3c7ffd4-4187-46fd-a590-99e2af539058"
DATASET_SLUG = "household-waste-recycling-centres"
DATAFILE_UUID = "1b582059-39b8-4b16-b37c-3f2d24610e9f"


@pytest.fixture(autouse=True)
def enable_solr_feature_flag(settings):
    settings.FEATURE_FLAGS_ENABLED = ["solr-search"]


@pytest.fixture
def preview_url():
    return reverse(
        "directory:preview",
        kwargs={"dataset_uuid": DATASET_UUID, "name": DATASET_SLUG, "datafile_uuid": DATAFILE_UUID},
    )


class TestPreviewPage:
    def test_heading_is_visible(self, page, live_server_url, preview_url):
        page.goto(live_server_url + preview_url)
        expect(page.get_by_role("heading", level=1)).to_contain_text("Household Waste Recycling Centres")

    def test_back_link_goes_to_dataset(self, page, live_server_url, preview_url):
        page.goto(live_server_url + preview_url)
        back_link = page.get_by_role("link", name="Back to dataset")
        expect(back_link).to_be_visible()
        expect(back_link).to_have_attribute(
            "href",
            reverse("directory:dataset", kwargs={"uuid": DATASET_UUID, "slug": DATASET_SLUG}),
        )
