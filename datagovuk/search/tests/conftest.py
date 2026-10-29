import importlib
from unittest.mock import MagicMock, patch

import pytest
from django.urls import clear_url_caches

import config.urls


def _filter_value(body, field):
    """
    Returns the value of the `{"term": {field: value}}` clause in the query's bool filter, if any.
    """
    for clause in body["query"]["bool"].get("filter", []):
        if field in clause.get("term", {}):
            return clause["term"][field]
    return None


@pytest.fixture
def set_search_v2_flag(settings):
    original_flags = settings.FEATURE_FLAGS_ENABLED

    def _set(enabled):
        settings.FEATURE_FLAGS_ENABLED = ["search-v2"] if enabled else []
        clear_url_caches()
        importlib.reload(config.urls)

    yield _set

    settings.FEATURE_FLAGS_ENABLED = original_flags
    clear_url_caches()
    importlib.reload(config.urls)


@pytest.fixture(autouse=True)
def search_v2_flag_enabled(set_search_v2_flag):
    set_search_v2_flag(enabled=True)


@pytest.fixture(autouse=True)
def mock_aws_sigv4_auth():
    with patch("datagovuk.search.opensearch.get_aws_sigv4_auth"):
        yield


@pytest.fixture(autouse=True)
def mock_opensearch_class(mock_aws_sigv4_auth):
    with patch("datagovuk.search.opensearch.OpenSearch") as mock:
        yield mock


@pytest.fixture
def mock_opensearch_client(mock_opensearch_class):
    """
    The client returned by `OpenSearch(...)`. Returns empty results unless `opensearch_documents` is used.
    """
    client = mock_opensearch_class.return_value
    client.search.return_value = {"hits": {"total": {"value": 0, "relation": "eq"}, "hits": []}}
    return client


@pytest.fixture
def opensearch_documents(mock_opensearch_client):
    """
    Factory fixture which loads documents into an in-memory stand in for the `datasets` index.
    """

    def _load(documents):
        def _search(index=None, body=None, **kwargs):
            assert index == "datasets"
            matching = [
                doc
                for doc in documents
                if all(_filter_value(body, field) in (None, doc.get(field)) for field in ("source", "slug"))
            ]
            hits = [{"_source": doc} for doc in matching[: body["size"]]]
            return {"hits": {"total": {"value": len(matching), "relation": "eq"}, "hits": hits}}

        mock_opensearch_client.search = MagicMock(side_effect=_search)
        return mock_opensearch_client

    return _load
