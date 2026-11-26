from http import HTTPStatus

import pytest
from django.urls import reverse

from datagovuk.search.opensearch import Collection, Dataset

from .factories import CollectionFactory, DatasetFactory, OrganisationFactory, ResourceFactory


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
        assert "search_query" not in response.context_data
        assert "directory_search" not in response.context_data
        assert "collection_search" not in response.context_data

    def test_get_with_query_searches_directory_and_collections(self, client, search_url, opensearch_documents):
        opensearch_documents(
            [
                DatasetFactory(slug="rail-data"),
                DatasetFactory(slug="bus-data"),
                CollectionFactory(slug="rail-collection", collection="transport"),
                CollectionFactory(slug="bus-collection", collection="transport"),
            ],
        )

        response = client.get(search_url, {"query": "rail"})

        assert response.status_code == HTTPStatus.OK
        context = response.context_data
        assert context["search_made"] is True
        assert context["search_query"] == "rail"
        assert [doc.slug for doc in context["directory_search"].docs] == ["rail-data"]
        assert [doc.slug for doc in context["collection_search"].docs] == ["rail-collection"]
        assert all(isinstance(doc, Dataset) for doc in context["directory_search"].docs)
        assert all(isinstance(doc, Collection) for doc in context["collection_search"].docs)
        assert context["directory_search"].total == 1
        assert context["collection_search"].total == 1

    def test_get_with_selected_facets_lists_filters_that_remove_themselves(
        self,
        client,
        search_url,
        opensearch_documents,
    ):
        publisher = OrganisationFactory(slug="ordnance-survey", name="Ordnance Survey")
        opensearch_documents([DatasetFactory(title="Rail data", organisations=[publisher])])

        response = client.get(search_url, {"query": "rail", "publisher": "ordnance-survey", "page": "2"})

        assert response.context_data["selected_filters"] == [
            {"key": "publisher", "label": "Ordnance Survey", "url": "?query=rail"},
        ]

    def test_get_groups_open_government_licence_and_no_links_in_more_filters(
        self,
        client,
        search_url,
        opensearch_documents,
    ):
        opensearch_documents([DatasetFactory(licence={"slug": "uk-ogl", "title": "Open Government Licence"})])

        response = client.get(search_url, {"query": ""})

        group = next(g for g in response.context_data["facet_groups"] if g["key"] == "other")
        assert group["label"] == "More filters"
        assert [(f["label"], f["url"]) for f in group["facets"]] == [
            ("Open Government Licence", "?query=&open_government_licence_only=on"),
            ("Include datasets with no links", "?query=&include_datasets_with_no_links=on"),
        ]

    def test_get_with_lowercase_facet_format_filters_directory_results(self, client, search_url, opensearch_documents):
        opensearch_documents(
            [
                DatasetFactory(slug="csv-data", resources=[ResourceFactory(format="CSV")]),
                DatasetFactory(slug="pdf-data", resources=[ResourceFactory(format="PDF")]),
            ],
        )

        response = client.get(search_url, {"query": "", "format": "csv"})

        assert response.status_code == HTTPStatus.OK
        assert [doc.slug for doc in response.context_data["directory_search"].docs] == ["csv-data"]

    def test_get_without_selected_facets_has_no_selected_filters(self, client, search_url, opensearch_documents):
        opensearch_documents([DatasetFactory()])

        response = client.get(search_url, {"query": "rail"})

        assert response.context_data["selected_filters"] == []

    @pytest.mark.parametrize("query", ["", "   "])
    def test_get_with_blank_query_matches_all(self, client, search_url, opensearch_documents, query):
        opensearch_documents(
            [
                DatasetFactory(slug="anything"),
                CollectionFactory(slug="any-collection", collection="transport"),
            ],
        )

        response = client.get(search_url, {"query": query})

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["search_made"] is True
        assert [doc.slug for doc in response.context_data["directory_search"].docs] == ["anything"]
        assert [doc.slug for doc in response.context_data["collection_search"].docs] == ["any-collection"]

    def test_get_with_no_results(self, client, search_url, opensearch_documents):
        opensearch_documents([DatasetFactory(), CollectionFactory()])

        response = client.get(search_url, {"query": "nothing matches"})

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["search_made"] is True
        assert response.context_data["directory_search"].docs == []
        assert response.context_data["collection_search"].docs == []
        assert response.context_data["directory_search"].total == 0
        assert response.context_data["collection_search"].total == 0

    def test_get_with_only_collection_results(self, client, search_url, opensearch_documents):
        opensearch_documents([CollectionFactory(slug="only-collection", collection="transport")])

        response = client.get(search_url, {"query": "collection"})

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["directory_search"].docs == []
        assert [doc.slug for doc in response.context_data["collection_search"].docs] == ["only-collection"]

    def test_get_with_only_directory_results(self, client, search_url, opensearch_documents):
        opensearch_documents([DatasetFactory(slug="only-directory")])

        response = client.get(search_url, {"query": "directory"})

        assert response.status_code == HTTPStatus.OK
        assert [doc.slug for doc in response.context_data["directory_search"].docs] == ["only-directory"]
        assert response.context_data["collection_search"].docs == []

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
        assert "search_query" not in response.context_data
        assert "directory_search" not in response.context_data

    def test_result_with_multiple_organisations_shows_first(self, client, search_url, opensearch_documents):
        organisations = [OrganisationFactory(name="First publisher"), OrganisationFactory(name="Second publisher")]
        opensearch_documents([DatasetFactory(title="Rail timetables", organisations=organisations)])

        response = client.get(search_url, {"query": "rail"})

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["directory_search"].docs[0].organisation.name == "First publisher"

    def test_get_with_filters_only_filters_directory_not_collections(self, client, search_url, opensearch_documents):
        opensearch_documents(
            [
                DatasetFactory(slug="transport", topic_slug="transport"),
                DatasetFactory(slug="health", topic_slug="health"),
                CollectionFactory(slug="any-collection", collection="transport"),
            ],
        )

        response = client.get(search_url, {"topic": "transport"})

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["search_made"] is True
        assert [doc.slug for doc in response.context_data["directory_search"].docs] == ["transport"]
        assert [doc.slug for doc in response.context_data["collection_search"].docs] == ["any-collection"]

    def test_get_with_publisher_filters_directory_results(self, client, search_url, opensearch_documents):
        opensearch_documents(
            [
                DatasetFactory(slug="wanted", organisations=[OrganisationFactory(slug="wanted-publisher")]),
                DatasetFactory(slug="other", organisations=[OrganisationFactory(slug="other-publisher")]),
            ],
        )

        response = client.get(search_url, {"publisher": "wanted-publisher"})

        assert response.status_code == HTTPStatus.OK
        assert [doc.slug for doc in response.context_data["directory_search"].docs] == ["wanted"]

    def test_get_with_format_filters_directory_results(self, client, search_url, opensearch_documents):
        opensearch_documents(
            [
                DatasetFactory(slug="csv", resources=[ResourceFactory(format="CSV")]),
                DatasetFactory(slug="pdf", resources=[ResourceFactory(format="PDF")]),
            ],
        )

        response = client.get(search_url, {"format": "CSV"})

        assert response.status_code == HTTPStatus.OK
        assert [doc.slug for doc in response.context_data["directory_search"].docs] == ["csv"]

    def test_get_with_open_government_licence_only_filters_directory_results(
        self,
        client,
        search_url,
        opensearch_documents,
    ):
        opensearch_documents(
            [
                DatasetFactory(slug="ogl", licence={"slug": "uk-ogl", "title": "Open Government Licence"}),
                DatasetFactory(slug="other", licence={"slug": "cc-by", "title": "Creative Commons"}),
            ],
        )

        response = client.get(search_url, {"open_government_licence_only": "on"})

        assert response.status_code == HTTPStatus.OK
        assert [doc.slug for doc in response.context_data["directory_search"].docs] == ["ogl"]

    def test_get_without_include_datasets_with_no_links_excludes_them(self, client, search_url, opensearch_documents):
        opensearch_documents([DatasetFactory(slug="with-links"), DatasetFactory(slug="no-links", resources=[])])

        response = client.get(search_url, {"query": ""})

        assert response.status_code == HTTPStatus.OK
        assert [doc.slug for doc in response.context_data["directory_search"].docs] == ["with-links"]

    def test_get_with_include_datasets_with_no_links_includes_them(self, client, search_url, opensearch_documents):
        opensearch_documents([DatasetFactory(slug="with-links"), DatasetFactory(slug="no-links", resources=[])])

        response = client.get(search_url, {"include_datasets_with_no_links": "on"})

        assert response.status_code == HTTPStatus.OK
        assert sorted(doc.slug for doc in response.context_data["directory_search"].docs) == ["no-links", "with-links"]

    def test_get_with_query_and_filters_combines_them(self, client, search_url, opensearch_documents):
        opensearch_documents(
            [
                DatasetFactory(slug="rail-transport", title="Rail timetables", topic_slug="transport"),
                DatasetFactory(slug="rail-health", title="Rail accidents", topic_slug="health"),
                DatasetFactory(slug="bus-transport", title="Bus routes", topic_slug="transport"),
            ],
        )

        response = client.get(search_url, {"query": "rail", "topic": "transport"})

        assert response.status_code == HTTPStatus.OK
        assert [doc.slug for doc in response.context_data["directory_search"].docs] == ["rail-transport"]

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("topic", "Transport"),
            ("topic", "not-a-topic"),
            ("format", "NOT-A-FORMAT"),
            ("publisher", "not a slug!"),
        ],
    )
    def test_get_with_invalid_filter_is_invalid(self, client, search_url, field, value):
        response = client.get(search_url, {field: value})

        assert response.status_code == HTTPStatus.OK
        assert response.template_name == ["search/search.jinja"]
        assert field in response.context_data["form"].errors
        assert "search_made" not in response.context_data
        assert "search_query" not in response.context_data
        assert "directory_search" not in response.context_data


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
        opensearch_documents([CollectionFactory(slug="wanted")])

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

    def test_get_dataset_harvested_true_is_in_context(self, client, opensearch_documents):
        opensearch_documents([DatasetFactory(slug="wanted", is_harvested=True)])

        response = client.get(reverse("search:dataset", kwargs={"slug": "wanted"}))

        assert response.context_data["doc"].is_harvested is True

    def test_get_dataset_harvested_false_is_in_context(self, client, opensearch_documents):
        opensearch_documents([DatasetFactory(slug="wanted", is_harvested=False)])

        response = client.get(reverse("search:dataset", kwargs={"slug": "wanted"}))

        assert response.context_data["doc"].is_harvested is False

    def test_get_dataset_additional_information_is_in_context(self, client, opensearch_documents):
        opensearch_documents(
            [
                DatasetFactory(
                    slug="wanted",
                    additional_information=[
                        {"key": "licence", "value": "OGL", "type": "string"},
                        {"key": "dataset-reference-date", "value": "invalid-json", "type": "json"},
                        {"key": "access_constraints", "value": '{"test-key": "test-value"}', "type": "json"},
                    ],
                ),
            ],
        )

        response = client.get(reverse("search:dataset", kwargs={"slug": "wanted"}))
        doc = response.context_data["doc"]
        additional_information = doc.additional_information

        assert response.status_code == HTTPStatus.OK
        assert response.template_name == ["search/dataset.jinja"]
        assert additional_information == {
            "licence": "OGL",
            "dataset-reference-date": "invalid-json",
            "access_constraints": {"test-key": "test-value"},
        }

    def test_get_dataset_resources_split_into_datafiles_and_docs(self, client, opensearch_documents):
        opensearch_documents(
            [
                DatasetFactory(
                    slug="wanted",
                    resources=[
                        ResourceFactory(name="My CSV", format="CSV", resource_type="data-link"),
                        ResourceFactory(name="My Doc", format="PDF", resource_type="supporting-document"),
                    ],
                ),
            ],
        )

        response = client.get(reverse("search:dataset", kwargs={"slug": "wanted"}))
        doc = response.context_data["doc"]

        assert response.status_code == HTTPStatus.OK
        assert len(doc.datafiles) == 1
        assert doc.datafiles[0].name == "My CSV"
        assert doc.datafiles[0].is_csv is True
        assert len(doc.docs) == 1
        assert doc.docs[0].name == "My Doc"
