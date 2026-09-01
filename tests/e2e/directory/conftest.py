import pytest
from django.urls import reverse

from datagovuk.directory.e2e_fixtures import DATASET_SLUG, DATASET_UUID


@pytest.fixture
def dataset_url():
    return reverse("directory:dataset", kwargs={"uuid": DATASET_UUID, "slug": DATASET_SLUG})
