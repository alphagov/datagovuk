import pysolr
import pytest


@pytest.fixture
def solr_url(settings):
    return settings.SOLR_URL + "-test"


@pytest.fixture(autouse=True)
def override_solr_settings(solr_url, settings):
    """
    Overrides Django settings for all tests to point to the temporary container.
    """
    settings.SOLR_URL = solr_url
    settings.FEATURE_FLAGS_ENABLED = [settings.FEATURE_FLAGS.SOLR_SEARCH.value]


@pytest.fixture
def solr_client(solr_url):
    """
    pysolr Client connected to the container.
    Wipes all Solr data before and after each test for test isolation.
    """
    client = pysolr.Solr(solr_url, always_commit=True)

    client.delete(q="*:*")
    yield client
    client.delete(q="*:*")


@pytest.fixture
def sample_solr_docs(solr_client):
    """
    Populates Solr with baseline sample data for testing.
    """
    docs = [
        {
            "id": "66c40d9c-bd29-42a9-9461-cd10d4898662",
            "state": "active",
            "type": "dataset",
            "title": "Test Dataset",
            "notes": "multi",
            "name": "test-dataset",
            "site_id": "default",
            "organisation": "regular_org",
        },
        {
            "id": "66c40d9c-bd29-42a9-9461-cd10d4898663",
            "state": "active",
            "type": "dataset",
            "title": "Other Dataset 2",
            "notes": "multi",
            "name": "test-dataset",
            "site_id": "default",
            "organisation": "regular_org",
        },
        {
            "id": "aa8a5b2c-8382-43f7-9f97-dee406c896c4",
            "state": "active",
            "title": "Excluded Dataset",
            "name": "excluded-dataset",
            "site_id": "dgu_organisations_123",
            "organisation": "dgu_organisations_123",
        },
    ]
    solr_client.add(docs)
    return docs
