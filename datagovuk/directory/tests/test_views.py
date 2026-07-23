import json
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
from django.urls import reverse


@pytest.fixture(autouse=True)
def directory_feature_flag(settings):
    settings.FEATURE_FLAGS_ENABLED = [settings.FEATURE_FLAGS.SOLR_SEARCH.value]


@pytest.fixture
def mock_solr_results_factory():
    """
    Factory fixture to create mock pysolr Results objects.
    """

    def _create(docs=None, hits=0):
        if docs is None:
            docs = []
        mock_results = MagicMock()
        mock_results.docs = docs
        mock_results.hits = hits
        return mock_results

    return _create


@pytest.fixture
def mock_solr_client(mock_solr_results_factory):
    """
    Mock pysolr client that returns empty results by default.
    """
    mock_client = MagicMock()
    mock_client.search.return_value = mock_solr_results_factory()
    return mock_client


@pytest.fixture(autouse=True)
def mock_get_solr_client(mock_solr_client):
    """
    Automatically mock get_solr_client for all tests in this module.
    """
    with patch("datagovuk.directory.views.get_solr_client", return_value=mock_solr_client):
        yield mock_solr_client


@pytest.fixture
def search_url():
    return reverse("directory:search")


class TestSearchView:
    def test_view_no_query_returns_ok_without_results(self, client, search_url):
        response = client.get(search_url)

        assert response.status_code == HTTPStatus.OK
        assert "results" not in response.context_data

    def test_view_with_query_calls_solr(self, client, sample_solr_docs, search_url):
        response = client.get(search_url, {"q": "test"})

        assert response.status_code == HTTPStatus.OK
        results = response.context_data["results"]
        assert results.hits == 1
        returned_doc = results.docs[0]
        assert returned_doc["id"] == "66c40d9c-bd29-42a9-9461-cd10d4898662"
        assert returned_doc["title"] == "Test Dataset"

        returned_ids = [doc["id"] for doc in results.docs]
        assert "test-uuid-2" not in returned_ids

    def test_view_with_query_no_hits_returns_empty(self, client, sample_solr_docs, search_url):
        response = client.get(search_url, {"q": "nomatch"})

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["results"].hits == 0
        assert response.context_data["results"].docs == []

    def test_view_with_query_multiple_results(self, client, sample_solr_docs, search_url):
        response = client.get(search_url, {"q": "multi"})

        assert response.status_code == HTTPStatus.OK
        expected_ids = [doc["id"] for doc in sample_solr_docs[0:2]]
        assert response.context_data["results"].hits == len(expected_ids)
        actual_ids = [doc["id"] for doc in response.context_data["results"].docs]
        assert actual_ids == expected_ids

    # def test_view_filter_publisher(self, client, sample_solr_docs):

    def test_search_view_returns_404_if_feature_flag_not_enabled(self, client, settings, search_url):
        settings.FEATURE_FLAGS_ENABLED = []
        response = client.get(search_url, {"q": "multi"})
        assert response.status_code == HTTPStatus.NOT_FOUND


class TestDatasetView:
    def test_view_existing_dataset_returns_ok(self, client, mock_solr_client, mock_solr_results_factory):
        test_uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_results = mock_solr_results_factory(
            docs=[
                {
                    "id": test_uuid,
                    "title": "Test Dataset",
                    "notes": "Test notes",
                    "metadata_modified": "2026-01-15T10:00:00Z",
                    "validated_data_dict": '{"organization": {"title": "Test Org"}, "resources": []}',
                },
            ],
            hits=1,
        )
        mock_solr_client.search.return_value = mock_results

        url = reverse("directory:dataset", kwargs={"uuid": test_uuid, "slug": "test-dataset"})
        response = client.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["document"]["title"] == "Test Dataset"
        assert response.context_data["document"]["notes"] == "Test notes"
        assert response.context_data["document"]["metadata_modified"] == "2026-01-15T10:00:00Z"
        assert response.context_data["document_data"]["organization"]["title"] == "Test Org"
        assert response.context_data["document_data"]["resources"] == []

    def test_view_existing_dataset_with_resources(self, client, mock_solr_client, mock_solr_results_factory):
        test_uuid = "550e8400-e29b-41d4-a716-446655440001"
        mock_results = mock_solr_results_factory(
            docs=[
                {
                    "id": test_uuid,
                    "title": "Dataset With Resources",
                    "notes": "Has resources",
                    "metadata_modified": "2026-02-20T15:30:00Z",
                    "validated_data_dict": (
                        '{"organization": {"title": "Publishing Org"}, '
                        '"resources": [{"name": "Data file", "url": "http://example.com/data.csv", '
                        '"resource_type": "CSV", "created": "2026-01-01"}]}'
                    ),
                },
            ],
            hits=1,
        )
        mock_solr_client.search.return_value = mock_results

        url = reverse("directory:dataset", kwargs={"uuid": test_uuid, "slug": "dataset-with-resources"})
        response = client.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["document"]["title"] == "Dataset With Resources"
        assert len(response.context_data["document_data"]["resources"]) == 1
        assert response.context_data["document_data"]["resources"][0]["name"] == "Data file"

    def test_view_nonexistent_dataset_returns_404(self, client, mock_solr_client, mock_solr_results_factory):
        mock_solr_client.search.return_value = mock_solr_results_factory(docs=[], hits=0)

        test_uuid = "00000000-0000-0000-0000-000000000000"
        url = reverse("directory:dataset", kwargs={"uuid": test_uuid, "slug": "nonexistent"})
        response = client.get(url)

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_view_dataset_solr_query_filters_by_id_and_state(self, client, mock_solr_client, mock_solr_results_factory):
        test_uuid = "550e8400-e29b-41d4-a716-446655440002"
        mock_solr_client.search.return_value = mock_solr_results_factory(
            docs=[
                {
                    "id": test_uuid,
                    "title": "Active Dataset",
                    "notes": "Active",
                    "metadata_modified": "2026-03-01T09:00:00Z",
                    "validated_data_dict": '{"organization": {"title": "Active Org"}, "resources": []}',
                },
            ],
            hits=1,
        )

        url = reverse("directory:dataset", kwargs={"uuid": test_uuid, "slug": "active-dataset"})
        client.get(url)

        call_args = mock_solr_client.search.call_args
        solr_query = call_args[0][0]
        assert f"id:{test_uuid}" in solr_query
        assert "state:active" in solr_query

    def test_dataset_view_returns_404_if_feature_flag_not_enabled(self, client, settings):
        settings.FEATURE_FLAGS_ENABLED = []
        test_uuid = "550e8400-e29b-41d4-a716-446655440002"
        url = reverse("directory:dataset", kwargs={"uuid": test_uuid, "slug": "active-dataset"})
        response = client.get(url)
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_csv_resource_shows_preview_link(self, client, mock_solr_client, mock_solr_results_factory):
        test_uuid = "550e8400-e29b-41d4-a716-446655440003"
        resource_uuid = "660e8400-e29b-41d4-a716-446655440003"
        mock_solr_client.search.return_value = mock_solr_results_factory(
            docs=[
                {
                    "id": test_uuid,
                    "name": "csv-dataset",
                    "title": "CSV Dataset",
                    "notes": "Has CSV",
                    "metadata_modified": "2026-01-01T00:00:00Z",
                    "validated_data_dict": json.dumps(
                        {
                            "organization": {"title": "Test Org"},
                            "resources": [
                                {
                                    "id": resource_uuid,
                                    "name": "Data",
                                    "url": "http://example.com/data.csv",
                                    "format": "CSV",
                                    "created": "2026-01-01",
                                },
                            ],
                        },
                    ),
                },
            ],
            hits=1,
        )

        url = reverse("directory:dataset", kwargs={"uuid": test_uuid, "slug": "csv-dataset"})
        response = client.get(url)

        expected_preview_url = reverse(
            "directory:preview",
            kwargs={"dataset_uuid": test_uuid, "name": "csv-dataset", "datafile_uuid": resource_uuid},
        )
        assert expected_preview_url in response.content.decode()

    def test_non_csv_resource_shows_not_available(self, client, mock_solr_client, mock_solr_results_factory):
        test_uuid = "550e8400-e29b-41d4-a716-446655440004"
        mock_solr_client.search.return_value = mock_solr_results_factory(
            docs=[
                {
                    "id": test_uuid,
                    "title": "XLS Dataset",
                    "notes": "Has XLS",
                    "metadata_modified": "2026-01-01T00:00:00Z",
                    "validated_data_dict": json.dumps(
                        {
                            "organization": {"title": "Test Org"},
                            "resources": [
                                {
                                    "id": "some-uuid",
                                    "name": "Data",
                                    "url": "http://example.com/data.xls",
                                    "format": "XLS",
                                    "created": "2026-01-01",
                                },
                            ],
                        },
                    ),
                },
            ],
            hits=1,
        )

        url = reverse("directory:dataset", kwargs={"uuid": test_uuid, "slug": "xls-dataset"})
        response = client.get(url)

        assert "Not available" in response.content.decode()
