from unittest.mock import MagicMock, patch

import pytest


def _filter_value(body, field):
    """
    Returns the value of the `{"term": {field: value}}` clause in the query's bool filter, if any.
    """
    for clause in body["query"]["bool"].get("filter", []):
        if field in clause.get("term", {}):
            return clause["term"][field]
    return None


@pytest.fixture(autouse=True)
def mock_opensearch_class():
    """
    Patches the OpenSearch class for every test so that nothing can reach a real cluster.
    """
    with patch("datagovuk.search.opensearch.OpenSearch") as mock_class:
        yield mock_class


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

    Documents are given as `_source` dicts (see `DatasetFactory`). The stand in applies the
    `source` and `slug` term filters and the `size` of a search request and returns an
    OpenSearch shaped response. It does no text matching or scoring - tests of how the query
    is built should assert on the body passed to `mock_opensearch_client.search`.
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
