import pytest
from django.urls import reverse
from playwright.sync_api import expect

from datagovuk.directory.e2e_fixtures import DATAFILE_UUID, DATASET_SLUG, DATASET_UUID


@pytest.fixture
def preview_url():
    return reverse(
        "directory:preview",
        kwargs={"dataset_uuid": DATASET_UUID, "name": DATASET_SLUG, "datafile_uuid": DATAFILE_UUID},
    )


class TestPreviewPage:
    def test_heading_is_visible(self, page, live_server_url, preview_url):
        page.goto(live_server_url + preview_url)
        expect(page.get_by_role("heading", level=1)).to_contain_text("Resource 2")

    def test_back_link_goes_to_dataset(self, page, live_server_url, preview_url):
        page.goto(live_server_url + preview_url)
        back_link = page.get_by_role("link", name="Back to dataset")
        expect(back_link).to_be_visible()
        expect(back_link).to_have_attribute(
            "href",
            reverse("directory:dataset", kwargs={"uuid": DATASET_UUID, "slug": DATASET_SLUG}),
        )
