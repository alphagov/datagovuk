import pysolr
import pytest
from django.core.cache import cache

from .factories import create_solr_doc


@pytest.fixture
def solr_url(settings):
    return settings.SOLR_URL


@pytest.fixture(autouse=True)
def override_solr_settings(solr_url, settings):
    """
    Overrides Django settings for all tests to point to the temporary container.
    """
    settings.SOLR_URL = solr_url


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
def solr_doc_factory(solr_client):

    def _create(**kwargs):
        doc = create_solr_doc(solr_client, **kwargs)
        # Not ideal, but we must clear the cache here so that `get_organisations_by_title()` provides updated results
        cache.clear()
        return doc

    return _create
