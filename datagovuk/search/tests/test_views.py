from http import HTTPStatus

import pytest
from django.urls import reverse

from datagovuk.search.opensearch import Dataset

from .factories import DatasetFactory, OrganisationFactory


@pytest.fixture
def search_url():
    return reverse("search:search")


class TestSearchView:
    def test_get_without_parameters_does_not_search(self, client, search_url, opensearch_documents):
        opensearch_documents([DatasetFactory()])

        response = client.get(search_url)

        assert response.status_code == HTTPStatus.OK
        assert response.template_name == ["search/search.jinja"]
        assert not response.context_data["form"].is_bound
        assert "search_made" not in response.context_data
        assert "directory_docs" not in response.context_data
        assert "collection_docs" not in response.context_data

    def test_get_with_query_searches_directory_and_collections(self, client, search_url, opensearch_documents):
        opensearch_documents(
            [
                DatasetFactory(source="ckan", slug="rail-data"),
                DatasetFactory(source="ckan", slug="bus-data"),
                DatasetFactory(source="collection", slug="rail-collection", collection="transport"),
                DatasetFactory(source="collection", slug="bus-collection", collection="transport"),
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

    @pytest.mark.parametrize("query", ["", "   "])
    def test_get_with_blank_query_matches_all(self, client, search_url, opensearch_documents, query):
        opensearch_documents(
            [
                DatasetFactory(source="ckan", slug="anything"),
                DatasetFactory(source="collection", slug="any-collection", collection="transport"),
            ],
        )

        response = client.get(search_url, {"query": query})

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["search_made"] is True
        assert [doc.slug for doc in response.context_data["directory_docs"]] == ["anything"]
        assert [doc.slug for doc in response.context_data["collection_docs"]] == ["any-collection"]

    def test_get_with_no_results(self, client, search_url, opensearch_documents):
        opensearch_documents([DatasetFactory(source="ckan"), DatasetFactory(source="collection")])

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

    def test_get_with_query_at_maximum_length_is_valid(self, client, search_url):
        response = client.get(search_url, {"query": "a" * 256})

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["search_made"] is True

    def test_get_with_query_over_maximum_length_is_invalid(self, client, search_url):
        response = client.get(search_url, {"query": "a" * 257})

        assert response.status_code == HTTPStatus.OK
        assert response.template_name == ["search/search.jinja"]
        assert "query" in response.context_data["form"].errors
        assert "search_made" not in response.context_data
        assert "directory_docs" not in response.context_data

    def test_result_with_multiple_organisations_shows_first(self, client, search_url, opensearch_documents):
        organisations = [OrganisationFactory(name="First publisher"), OrganisationFactory(name="Second publisher")]
        opensearch_documents([DatasetFactory(title="Rail timetables", organisations=organisations)])

        response = client.get(search_url, {"query": "rail"})

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["directory_docs"][0].organisation.name == "First publisher"


class TestDatasetView:
    def test_get_existing_dataset(self, client, opensearch_documents):
        opensearch_documents([DatasetFactory(slug="wanted", title="Wanted dataset"), DatasetFactory(slug="other")])

        response = client.get(reverse("search:dataset", kwargs={"slug": "wanted"}))

        assert response.status_code == HTTPStatus.OK
        assert response.template_name == ["search/dataset.jinja"]
        doc = response.context_data["doc"]
        assert isinstance(doc, Dataset)
        assert doc.slug == "wanted"
        assert doc.title == "Wanted dataset"

    def test_get_unknown_dataset_is_not_found(self, client, opensearch_documents):
        opensearch_documents([DatasetFactory(slug="other")])

        response = client.get(reverse("search:dataset", kwargs={"slug": "wanted"}))

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_get_collection_document_is_not_found(self, client, opensearch_documents):
        opensearch_documents([DatasetFactory(slug="wanted", source="collection")])

        response = client.get(reverse("search:dataset", kwargs={"slug": "wanted"}))

        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize(
        ("url_slug", "indexed_slug"),
        [("a b", "a b"), ("a.b", "a.b"), ("a%2Fb", "a/b"), ("caf%C3%A9", "café")],
    )
    def test_get_with_invalid_slug_is_not_found(self, client, opensearch_documents, url_slug, indexed_slug):
        opensearch_documents([DatasetFactory(slug=indexed_slug)])

        response = client.get(f"/v2/dataset/{url_slug}")

        assert response.status_code == HTTPStatus.NOT_FOUND
