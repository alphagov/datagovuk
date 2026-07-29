import pytest
from django.urls import reverse
from playwright.sync_api import expect

DATASET_UUID = "055e9bd9-756b-46e5-a8d6-9369184273ba"
DATASET_SLUG = "nhs-england-clinical-commissiong-group-and-local-authority-information-packs"
DATAFILE_UUID = "160e549b-6016-4036-873a-1d8ef951eb8e"


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
        expect(page.get_by_role("heading", level=1)).to_contain_text("CCG Data file")

    def test_back_link_goes_to_dataset(self, page, live_server_url, preview_url):
        page.goto(live_server_url + preview_url)
        back_link = page.get_by_role("link", name="Back to dataset")
        expect(back_link).to_be_visible()
        expect(back_link).to_have_attribute(
            "href",
            reverse("directory:dataset", kwargs={"uuid": DATASET_UUID, "slug": DATASET_SLUG}),
        )
