from unittest.mock import MagicMock, patch

import pytest
from opensearchpy import RequestsHttpConnection
from pydantic import ValidationError

from datagovuk.search.opensearch import (
    Dataset,
    get_aws_sigv4_auth,
    get_directory_document_by_slug,
    get_opensearch_client,
    search_collections,
    search_directory,
)

from .factories import DatasetFactory

COLLECTION_RESULTS = 2
DIRECTORY_RESULTS = 20
EXTRA_RESULTS = 3


def _request_body(client):
    client.search.assert_called_once()
    return client.search.call_args.kwargs["body"]


@patch("datagovuk.search.opensearch.get_aws_sigv4_auth")
def test_get_opensearch_client(mock_auth, settings, mock_opensearch_class):
    settings.OPENSEARCH_URL = "http://opensearch.example.com:9200"
    settings.AWS_OPENSEARCH_USE_SSL = False
    settings.AWS_OPENSEARCH_VERIFY_CERTS = False
    mock_auth.return_value = MagicMock()

    client = get_opensearch_client()

    assert client == mock_opensearch_class.return_value
    mock_opensearch_class.assert_called_once_with(
        hosts=["http://opensearch.example.com:9200"],
        use_ssl=False,
        verify_certs=False,
        connection_class=RequestsHttpConnection,
        http_auth=mock_auth.return_value,
    )


@patch("datagovuk.search.opensearch.get_aws_sigv4_auth")
def test_get_opensearch_client_uses_ssl_settings(mock_auth, settings, mock_opensearch_class):
    settings.OPENSEARCH_URL = "http://opensearch.example.com:9200"
    settings.AWS_OPENSEARCH_USE_SSL = True
    settings.AWS_OPENSEARCH_VERIFY_CERTS = True

    get_opensearch_client()

    opensearch_args = mock_opensearch_class.call_args.kwargs
    assert opensearch_args["use_ssl"] is True
    assert opensearch_args["verify_certs"] is True


@patch("datagovuk.search.opensearch.boto3.Session")
@patch("datagovuk.search.opensearch.AWSV4SignerAuth")
def test_get_aws_sigv4_auth(mock_auth_class, mock_session, settings):
    settings.AWS_REGION = "eu-west-0"
    mock_credentials = MagicMock()

    mock_session.return_value.get_credentials.return_value = mock_credentials
    auth = get_aws_sigv4_auth()

    mock_auth_class.assert_called_once_with(mock_credentials, "eu-west-0")
    assert auth == mock_auth_class.return_value


def test_search_collections_with_query_uses_multi_match_on_title_fields(mock_opensearch_client):
    search_collections("rail timetables")

    must = _request_body(mock_opensearch_client)["query"]["bool"]["must"]
    assert must == [
        {
            "multi_match": {
                "query": "rail timetables",
                "fields": ["title^3", "title.english^2"],
                "type": "best_fields",
            },
        },
    ]


def test_search_collections_passes_query_through_unchanged(mock_opensearch_client):
    search_collections("  rail  ")

    must = _request_body(mock_opensearch_client)["query"]["bool"]["must"]
    assert must[0]["multi_match"]["query"] == "  rail  "


@pytest.mark.parametrize("query", [None, "", " ", " \t\n "])
def test_search_collections_with_blank_query_matches_all(query, mock_opensearch_client):
    search_collections(query)

    must = _request_body(mock_opensearch_client)["query"]["bool"]["must"]
    assert must == [{"match_all": {}}]


@pytest.mark.parametrize("query", ["rail", ""])
def test_search_collections_is_limited_to_collection_source_and_two_hits(query, mock_opensearch_client):
    search_collections(query)

    call = mock_opensearch_client.search.call_args
    assert call.kwargs["index"] == "datasets"
    assert call.kwargs["body"]["query"]["bool"]["filter"] == [{"term": {"source": "collection"}}]
    assert call.kwargs["body"]["size"] == COLLECTION_RESULTS


def test_search_collections_returns_raw_response_and_documents_in_hit_order(mock_opensearch_client):
    hits = [{"_source": DatasetFactory(slug=f"collection-{i}", source="collection")} for i in range(2)]
    raw_response = {"hits": {"total": {"value": 2}, "hits": hits}}
    mock_opensearch_client.search.return_value = raw_response

    response, results = search_collections("collection")

    assert response is raw_response
    assert all(isinstance(result, Dataset) for result in results)
    assert [result.slug for result in results] == ["collection-0", "collection-1"]


def test_search_collections_without_hits_returns_no_documents(mock_opensearch_client):
    response, results = search_collections("nothing matches")

    assert response["hits"]["total"]["value"] == 0
    assert results == []


def test_search_collections_with_invalid_hit_raises(mock_opensearch_client):
    invalid_hit = {"_source": {"slug": "missing-everything-else"}}
    mock_opensearch_client.search.return_value = {"hits": {"total": {"value": 1}, "hits": [invalid_hit]}}

    with pytest.raises(ValidationError):
        search_collections("rail")


def test_search_collections_only_returns_collection_documents(opensearch_documents):
    opensearch_documents(
        [
            DatasetFactory(source="ckan", slug="from-ckan"),
            DatasetFactory(source="collection", slug="from-collection"),
        ],
    )

    _, results = search_collections("")

    assert [result.slug for result in results] == ["from-collection"]


def test_search_collections_limits_documents_but_not_total(opensearch_documents):
    opensearch_documents([DatasetFactory(source="collection") for _ in range(COLLECTION_RESULTS + EXTRA_RESULTS)])

    response, results = search_collections("")

    assert len(results) == COLLECTION_RESULTS
    assert response["hits"]["total"]["value"] == COLLECTION_RESULTS + EXTRA_RESULTS


def test_search_directory_with_query_uses_multi_match_on_title_and_description_fields(mock_opensearch_client):
    search_directory("rail timetables")

    must = _request_body(mock_opensearch_client)["query"]["bool"]["must"]
    assert must == [
        {
            "multi_match": {
                "query": "rail timetables",
                "fields": ["title^3", "title.english^2", "description", "description.english"],
                "type": "best_fields",
            },
        },
    ]


def test_search_directory_passes_query_through_unchanged(mock_opensearch_client):
    search_directory("  rail  ")

    must = _request_body(mock_opensearch_client)["query"]["bool"]["must"]
    assert must[0]["multi_match"]["query"] == "  rail  "


@pytest.mark.parametrize("query", [None, "", " ", " \t\n "])
def test_search_directory_with_blank_query_matches_all(query, mock_opensearch_client):
    search_directory(query)

    must = _request_body(mock_opensearch_client)["query"]["bool"]["must"]
    assert must == [{"match_all": {}}]


@pytest.mark.parametrize("query", ["rail", ""])
def test_search_directory_is_limited_to_ckan_source_and_twenty_hits(query, mock_opensearch_client):
    search_directory(query)

    call = mock_opensearch_client.search.call_args
    assert call.kwargs["index"] == "datasets"
    assert call.kwargs["body"]["query"]["bool"]["filter"] == [{"term": {"source": "ckan"}}]
    assert call.kwargs["body"]["size"] == DIRECTORY_RESULTS


def test_search_directory_returns_raw_response_and_documents_in_hit_order(mock_opensearch_client):
    hits = [{"_source": DatasetFactory(slug=f"dataset-{i}")} for i in range(2)]
    raw_response = {"hits": {"total": {"value": 2}, "hits": hits}}
    mock_opensearch_client.search.return_value = raw_response

    response, results = search_directory("dataset")

    assert response is raw_response
    assert all(isinstance(result, Dataset) for result in results)
    assert [result.slug for result in results] == ["dataset-0", "dataset-1"]


def test_search_directory_without_hits_returns_no_documents(mock_opensearch_client):
    response, results = search_directory("nothing matches")

    assert response["hits"]["total"]["value"] == 0
    assert results == []


def test_search_directory_with_invalid_hit_raises(mock_opensearch_client):
    invalid_hit = {"_source": {"slug": "missing-everything-else"}}
    mock_opensearch_client.search.return_value = {"hits": {"total": {"value": 1}, "hits": [invalid_hit]}}

    with pytest.raises(ValidationError):
        search_directory("rail")


def test_search_directory_only_returns_ckan_documents(opensearch_documents):
    opensearch_documents(
        [
            DatasetFactory(source="ckan", slug="from-ckan"),
            DatasetFactory(source="collection", slug="from-collection"),
        ],
    )

    _, results = search_directory("")

    assert [result.slug for result in results] == ["from-ckan"]


def test_search_directory_limits_documents_but_not_total(opensearch_documents):
    opensearch_documents([DatasetFactory(source="ckan") for _ in range(DIRECTORY_RESULTS + EXTRA_RESULTS)])

    response, results = search_directory("")

    assert len(results) == DIRECTORY_RESULTS
    assert response["hits"]["total"]["value"] == DIRECTORY_RESULTS + EXTRA_RESULTS


def test_get_directory_document_by_slug_found(opensearch_documents):
    opensearch_documents([DatasetFactory(slug="wanted", title="Wanted dataset"), DatasetFactory(slug="other")])

    document = get_directory_document_by_slug("wanted")

    assert isinstance(document, Dataset)
    assert document.slug == "wanted"
    assert document.title == "Wanted dataset"


def test_get_directory_document_by_slug_not_found(opensearch_documents):
    opensearch_documents([DatasetFactory(slug="other")])

    assert get_directory_document_by_slug("wanted") is None


def test_get_directory_document_by_slug_filters_on_slug_and_ckan_source(mock_opensearch_client):
    get_directory_document_by_slug("wanted")

    call = mock_opensearch_client.search.call_args
    assert call.kwargs["index"] == "datasets"
    assert call.kwargs["body"] == {
        "query": {"bool": {"filter": [{"term": {"slug": "wanted"}}, {"term": {"source": "ckan"}}]}},
        "size": 1,
    }


def test_get_directory_document_by_slug_ignores_collection_document_with_same_slug(opensearch_documents):
    opensearch_documents([DatasetFactory(slug="wanted", source="collection")])

    assert get_directory_document_by_slug("wanted") is None


def test_get_directory_document_by_slug_uses_first_hit(mock_opensearch_client):
    hits = [{"_source": DatasetFactory(slug="first")}, {"_source": DatasetFactory(slug="second")}]
    mock_opensearch_client.search.return_value = {"hits": {"total": {"value": 2}, "hits": hits}}

    document = get_directory_document_by_slug("first")

    assert document.slug == "first"


def test_get_directory_document_by_slug_with_invalid_document_raises(mock_opensearch_client):
    mock_opensearch_client.search.return_value = {"hits": {"total": {"value": 1}, "hits": [{"_source": {}}]}}

    with pytest.raises(ValidationError):
        get_directory_document_by_slug("wanted")
