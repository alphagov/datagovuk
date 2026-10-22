from http import HTTPStatus

import pytest
from django.urls import reverse

from datagovuk.search.opensearch import Dataset

from .factories import DatasetFactory, OrganisationFactory


@pytest.fixture
def search_url():
    return reverse("search:search")


def _queries_sent(client):
    """
    The text of each search sent to OpenSearch, with `None` standing in for `match_all`.
    """
    queries = []
    for call in client.search.call_args_list:
        must = call.kwargs["body"]["query"]["bool"]["must"][0]
        queries.append(must.get("multi_match", {}).get("query"))
    return queries


class TestSearchView:
    def test_get_without_parameters_does_not_search(self, client, search_url, mock_opensearch_client):
        response = client.get(search_url)

        assert response.status_code == HTTPStatus.OK
        assert response.template_name == ["search/search.jinja"]
        assert not response.context_data["form"].is_bound
        assert "search_made" not in response.context_data
        mock_opensearch_client.search.assert_not_called()

    def test_get_with_query_searches_directory_and_collections(self, client, search_url, opensearch_documents):
        client_mock = opensearch_documents(
            [
                DatasetFactory(source="ckan", slug="rail-data"),
                DatasetFactory(source="collection", slug="rail-collection", collection="transport"),
            ],
        )

        response = client.get(search_url, {"query": "rail"})

        assert response.status_code == HTTPStatus.OK
        context = response.context_data
        assert context["search_made"] is True
        assert context["form"].cleaned_data["query"] == "rail"
        assert [doc.slug for doc in context["directory_docs"]] == ["rail-data"]
        assert [doc.slug for doc in context["collection_docs"]] == ["rail-collection"]
        assert all(isinstance(doc, Dataset) for doc in [*context["directory_docs"], *context["collection_docs"]])
        assert context["directory_results"]["hits"]["total"]["value"] == 1
        assert context["collection_results"]["hits"]["total"]["value"] == 1
        assert _queries_sent(client_mock) == ["rail", "rail"]

    @pytest.mark.parametrize("query", ["", "   "])
    def test_get_with_blank_query_matches_all(self, client, search_url, opensearch_documents, query):
        client_mock = opensearch_documents([DatasetFactory(slug="anything")])

        response = client.get(search_url, {"query": query})

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["search_made"] is True
        assert [doc.slug for doc in response.context_data["directory_docs"]] == ["anything"]
        assert _queries_sent(client_mock) == [None, None]

    def test_get_with_no_results(self, client, search_url, mock_opensearch_client):
        response = client.get(search_url, {"query": "nothing matches"})

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["search_made"] is True
        assert response.context_data["directory_docs"] == []
        assert response.context_data["collection_docs"] == []
        assert response.context_data["directory_results"]["hits"]["total"]["value"] == 0
        assert response.context_data["collection_results"]["hits"]["total"]["value"] == 0

    def test_get_with_only_collection_results(self, client, search_url, opensearch_documents):
        opensearch_documents([DatasetFactory(source="collection", slug="only-collection", collection="transport")])

        response = client.get(search_url, {"query": "collection"})

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["directory_docs"] == []
        assert [doc.slug for doc in response.context_data["collection_docs"]] == ["only-collection"]

    def test_get_with_only_directory_results(self, client, search_url, opensearch_documents):
        opensearch_documents([DatasetFactory(source="ckan", slug="only-directory")])

        response = client.get(search_url, {"query": "directory"})

        assert response.status_code == HTTPStatus.OK
        assert [doc.slug for doc in response.context_data["directory_docs"]] == ["only-directory"]
        assert response.context_data["collection_docs"] == []

    def test_get_with_query_at_maximum_length_is_valid(self, client, search_url, mock_opensearch_client):
        response = client.get(search_url, {"query": "a" * 256})

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["search_made"] is True

    def test_get_with_query_over_maximum_length_is_invalid(self, client, search_url, mock_opensearch_client):
        response = client.get(search_url, {"query": "a" * 257})

        assert response.status_code == HTTPStatus.OK
        assert response.template_name == ["search/search.jinja"]
        assert "query" in response.context_data["form"].errors
        assert "search_made" not in response.context_data
        mock_opensearch_client.search.assert_not_called()

    def test_result_with_multiple_organisations_shows_first(self, client, search_url, opensearch_documents):
        organisations = [OrganisationFactory(name="First publisher"), OrganisationFactory(name="Second publisher")]
        opensearch_documents([DatasetFactory(organisations=organisations)])

        response = client.get(search_url, {"query": "anything"})

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["directory_docs"][0].organisation.name == "First publisher"


class TestDatasetView:
    def test_get_existing_dataset(self, client, opensearch_documents):
        opensearch_documents([DatasetFactory(slug="wanted", title="Wanted dataset")])

        response = client.get(reverse("search:dataset", kwargs={"slug": "wanted"}))

        assert response.status_code == HTTPStatus.OK
        assert response.template_name == ["search/dataset.jinja"]
        doc = response.context_data["doc"]
        assert isinstance(doc, Dataset)
        assert doc.slug == "wanted"
        assert doc.title == "Wanted dataset"

    def test_get_looks_up_slug_from_url(self, client, opensearch_documents):
        client_mock = opensearch_documents([DatasetFactory(slug="wanted")])

        response = client.get(reverse("search:dataset", kwargs={"slug": "wanted"}))

        filters = client_mock.search.call_args.kwargs["body"]["query"]["bool"]["filter"]
        assert {"term": {"slug": "wanted"}} in filters
        assert response.status_code == HTTPStatus.OK

    def test_get_unknown_dataset_is_not_found(self, client, opensearch_documents):
        opensearch_documents([DatasetFactory(slug="other")])

        response = client.get(reverse("search:dataset", kwargs={"slug": "wanted"}))

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_get_collection_document_is_not_found(self, client, opensearch_documents):
        opensearch_documents([DatasetFactory(slug="wanted", source="collection")])

        response = client.get(reverse("search:dataset", kwargs={"slug": "wanted"}))

        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize("slug", ["a b", "a.b", "a%2Fb", "caf%C3%A9"])
    def test_get_with_invalid_slug_is_not_found_without_searching(self, client, mock_opensearch_client, slug):
        response = client.get(f"/v2/dataset/{slug}")

        assert response.status_code == HTTPStatus.NOT_FOUND
        mock_opensearch_client.search.assert_not_called()
