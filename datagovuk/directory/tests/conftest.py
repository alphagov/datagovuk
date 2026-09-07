import pysolr
import pytest
import requests
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
    solr_base_url_end = solr_url.rfind("/solr") + 5
    solr_base_url = solr_url[:solr_base_url_end]
    solr_core_name = solr_url[solr_base_url_end + 1 :]
    # Create solr test core...
    params = {
        "action": "CREATE",
        "name": solr_core_name,
        "configSet": "ckan-template",
        "wt": "json",
    }
    requests.get(f"{solr_base_url}/admin/cores", params=params)  # noqa: S113
    client = pysolr.Solr(solr_url, always_commit=True)

    client.delete(q="*:*")
    yield client
    client.delete(q="*:*")

    params = {
        "action": "UNLOAD",
        "core": solr_core_name,
        "deleteIndex": "true",
        "deleteInstanceDir": "true",
        "wt": "json",
    }
    requests.get(f"{solr_base_url}/admin/cores", params=params)  # noqa: S113


@pytest.fixture
def solr_doc_factory(solr_client):

    def _create(**kwargs):
        doc = create_solr_doc(solr_client, **kwargs)
        # Not ideal, but we must clear the cache here so that `get_organisations_by_title()` provides updated results
        cache.clear()
        return doc

    return _create
