import json
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
from django.http import HttpResponseNotFound, HttpResponsePermanentRedirect
from django.urls import NoReverseMatch, reverse


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
    def test_search_view_sort_recent_orders_by_metadata_modified_descending(
        self,
        client,
        solr_doc_factory,
        search_url,
    ):
        doc_recent = solr_doc_factory(title="recent-dataset", metadata_modified="2026-07-30T00:00:00Z")
        doc_older = solr_doc_factory(title="older-dataset", metadata_modified="2025-01-01T00:00:00Z")

        response = client.get(search_url, {"q": "dataset", "sort": "recent"})

        assert response.status_code == HTTPStatus.OK
        actual_ids = [doc["id"] for doc in response.context_data["results"].docs]
        assert actual_ids == [doc_recent["id"], doc_older["id"]]

    def test_view_no_query_returns_ok_without_results(self, client, solr_doc_factory, search_url):
        solr_doc_factory()

        response = client.get(search_url)

        assert response.status_code == HTTPStatus.OK
        assert "results" not in response.context_data

    def test_view_empty_query_returns_ok_all_results(self, client, solr_doc_factory, search_url):
        solr_doc_factory()

        response = client.get(search_url, {"query": ""})

        assert response.status_code == HTTPStatus.OK
        assert "results" in response.context_data
        assert response.context_data["results"].hits == 1

    def test_view_with_query_calls_solr(self, client, solr_doc_factory, search_url):
        matching_doc = solr_doc_factory(title="test")
        solr_doc_factory()

        response = client.get(search_url, {"q": "test"})

        assert response.status_code == HTTPStatus.OK
        results = response.context_data["results"]
        assert results.hits == 1
        returned_doc = results.docs[0]
        assert returned_doc["id"] == matching_doc["id"]
        assert returned_doc["title"] == matching_doc["title"]

    def test_view_with_query_no_hits_returns_empty(self, client, solr_doc_factory, search_url):
        solr_doc_factory()
        solr_doc_factory()

        response = client.get(search_url, {"q": "nomatch"})

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["results"].hits == 0
        assert response.context_data["results"].docs == []

    def test_view_with_query_only_stop_words_returns_empty(self, client, solr_doc_factory, search_url):
        solr_doc_factory()

        response = client.get(search_url, {"q": "of the and a is"})

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["results"].hits == 0
        assert response.context_data["results"].docs == []

    def test_view_with_query_multiple_results(self, client, solr_doc_factory, search_url):
        matching_doc = solr_doc_factory(notes="multi")
        matching_doc_2 = solr_doc_factory(title="multi")
        solr_doc_factory()

        response = client.get(search_url, {"q": "multi"})

        assert response.status_code == HTTPStatus.OK
        expected_ids = [matching_doc["id"], matching_doc_2["id"]]
        actual_ids = [doc["id"] for doc in response.context_data["results"].docs]
        assert set(actual_ids) == set(expected_ids)

    def test_view_filter_publisher_documents_match(self, client, solr_doc_factory, search_url):
        matching_doc = solr_doc_factory(organization="regular-publisher")
        solr_doc_factory(organization="regular-publisher-2")

        response = client.get(search_url, {"q": "dataset", "publisher": "Regular publisher"})

        assert response.status_code == HTTPStatus.OK
        expected_ids = [matching_doc["id"]]
        actual_ids = [doc["id"] for doc in response.context_data["results"].docs]
        assert actual_ids == expected_ids

    def test_view_filter_publisher_no_documents_match(self, client, solr_doc_factory, search_url):
        solr_doc_factory()
        solr_doc_factory()

        response = client.get(search_url, {"q": "multi", "publisher": "Non-existent"})
        assert response.status_code == HTTPStatus.OK
        assert "results" not in response.context_data
        assert response.context_data["form"].errors["publisher"] == [
            "Select a valid choice. Non-existent is not one of the available choices.",
        ]

    def test_view_filter_open_government_licence_only(self, client, solr_doc_factory, search_url):
        matching_doc = solr_doc_factory(license_id="ogl")
        solr_doc_factory()

        response = client.get(search_url, {"q": "dataset", "open_government_licence_only": "on"})

        assert response.status_code == HTTPStatus.OK
        expected_ids = [matching_doc["id"]]
        actual_ids = [doc["id"] for doc in response.context_data["results"].docs]
        assert actual_ids == expected_ids

    def test_view_filter_topic(self, client, solr_doc_factory, search_url):
        matching_doc = solr_doc_factory(topic="environment")
        solr_doc_factory()

        response = client.get(search_url, {"q": "dataset", "topic": "Environment"})

        assert response.status_code == HTTPStatus.OK
        expected_ids = [matching_doc["id"]]
        actual_ids = [doc["id"] for doc in response.context_data["results"].docs]
        assert actual_ids == expected_ids

    def test_view_filter_topic_overlapping_topic_terms_match_correctly(self, client, solr_doc_factory, search_url):
        matching_doc = solr_doc_factory(topic="business-and-economy")
        solr_doc_factory(topic="crime-and-justice")
        solr_doc_factory()

        response = client.get(search_url, {"q": "dataset", "topic": "Business and economy"})

        assert response.status_code == HTTPStatus.OK
        expected_ids = [matching_doc["id"]]
        actual_ids = [doc["id"] for doc in response.context_data["results"].docs]
        assert actual_ids == expected_ids

    def test_view_filter_format_matching_mapped_format(self, client, solr_doc_factory, search_url):
        matching_document = solr_doc_factory(res_format=[".csv"])
        solr_doc_factory(res_format=["XLSX"])

        response = client.get(search_url, {"q": "dataset", "format": "CSV"})

        assert response.status_code == HTTPStatus.OK
        expected_ids = [matching_document["id"]]
        actual_ids = [doc["id"] for doc in response.context_data["results"].docs]
        assert actual_ids == expected_ids

    def test_view_filter_format_matching_other_format(self, client, solr_doc_factory, search_url):
        matching_document = solr_doc_factory(res_format=["woop"])
        solr_doc_factory(res_format=["XLS"])

        response = client.get(search_url, {"q": "dataset", "format": "OTHER"})

        assert response.status_code == HTTPStatus.OK
        expected_ids = [matching_document["id"]]
        actual_ids = [doc["id"] for doc in response.context_data["results"].docs]
        assert actual_ids == expected_ids

    def test_search_view_returns_error_if_form_invalid(self, client, search_url):
        response = client.get(search_url, {"q": "multi" * 200})
        assert response.status_code == HTTPStatus.OK
        assert response.context_data["form"].errors["query"] == [
            "Ensure this value has at most 256 characters (it has 1000).",
        ]

    def test_search_view_facets_not_applied_when_empty_results(self, client, solr_doc_factory, search_url):
        solr_doc_factory(
            organization="my-publisher",
            topic="Environment",
            res_format=["CSV", "JSON"],
        )
        solr_doc_factory(
            organization="my-publisher",
            topic="Environment",
            res_format=["CSV", "JSON", "XLS"],
        )
        response = client.get(search_url, {"q": "nomatch", "format": "CSV"})
        assert response.status_code == HTTPStatus.OK
        assert response.context_data["form"].errors == {}

    def test_search_view_facets_reduce_with_filtering(self, client, solr_doc_factory, search_url):
        doc_1 = solr_doc_factory(
            name="test",
            organization="some-other-publisher",
        )
        doc_2 = solr_doc_factory(
            name="test",
            organization="my-publisher",
        )
        doc_3 = solr_doc_factory(
            name="test",
            organization="my-publisher",
            topic="Environment",
        )
        doc_4 = solr_doc_factory(
            name="test",
            organization="my-publisher",
            topic="Business and economy",
            res_format=["JSON"],
        )
        doc_5 = solr_doc_factory(
            name="test",
            organization="my-publisher",
            topic="Environment",
            res_format=["CSV", "JSON"],
        )
        doc_6 = solr_doc_factory(
            name="test",
            organization="my-publisher",
            topic="Environment",
            res_format=["CSV", "JSON", "XLS"],
        )

        query = "test"
        # Firstly search for all 'test' records...
        response = client.get(search_url, {"q": query})
        assert [doc["id"] for doc in response.context_data["results"].docs] == [
            doc_1["id"],
            doc_2["id"],
            doc_3["id"],
            doc_4["id"],
            doc_5["id"],
            doc_6["id"],
        ]
        assert response.context_data["form"].fields["publisher"].choices == [
            ("", ""),
            ("My publisher", "My publisher"),
            ("Some other publisher", "Some other publisher"),
        ]
        assert response.context_data["form"].fields["topic"].choices == [
            ("", ""),
            ("Environment", "Environment"),
            ("Business and economy", "Business and economy"),
        ]
        assert response.context_data["form"].fields["format"].choices == [
            ("", ""),
            ("JSON", "JSON"),
            ("CSV", "CSV"),
            ("XLS", "XLS"),
        ]

        # Next filter by publisher...
        response = client.get(search_url, {"q": query, "publisher": "My publisher"})
        assert [doc["id"] for doc in response.context_data["results"].docs] == [
            doc_2["id"],
            doc_3["id"],
            doc_4["id"],
            doc_5["id"],
            doc_6["id"],
        ]
        assert response.context_data["form"].fields["publisher"].choices == [("", ""), ("My publisher", "My publisher")]
        assert response.context_data["form"].fields["topic"].choices == [
            ("", ""),
            ("Environment", "Environment"),
            ("Business and economy", "Business and economy"),
        ]
        assert response.context_data["form"].fields["format"].choices == [
            ("", ""),
            ("JSON", "JSON"),
            ("CSV", "CSV"),
            ("XLS", "XLS"),
        ]

        # Next filter by publisher and topic...
        response = client.get(search_url, {"q": query, "publisher": "My publisher", "topic": "Environment"})
        assert [doc["id"] for doc in response.context_data["results"].docs] == [doc_3["id"], doc_5["id"], doc_6["id"]]
        assert response.context_data["form"].fields["publisher"].choices == [("", ""), ("My publisher", "My publisher")]
        assert response.context_data["form"].fields["topic"].choices == [("", ""), ("Environment", "Environment")]
        assert response.context_data["form"].fields["format"].choices == [
            ("", ""),
            ("CSV", "CSV"),
            ("JSON", "JSON"),
            ("XLS", "XLS"),
        ]

        # Next filter by publisher, topic and format...
        response = client.get(
            search_url,
            {"q": query, "publisher": "My publisher", "topic": "Environment", "format": "XLS"},
        )
        assert [doc["id"] for doc in response.context_data["results"].docs] == [doc_6["id"]]
        assert response.context_data["form"].fields["publisher"].choices == [("", ""), ("My publisher", "My publisher")]
        assert response.context_data["form"].fields["topic"].choices == [("", ""), ("Environment", "Environment")]
        assert response.context_data["form"].fields["format"].choices == [
            ("", ""),
            ("CSV", "CSV"),
            ("JSON", "JSON"),
            ("XLS", "XLS"),
        ]

    def test_page_overflow_does_not_raise_solr_error(self, client, solr_doc_factory, search_url):
        solr_doc_factory(title="test")

        response = client.get(search_url, {"q": "test", "page": "2333300000"})

        assert response.status_code == HTTPStatus.FOUND

    def test_page_exceeding_max_page_redirects_to_last_page(self, client, solr_doc_factory, search_url):
        for _ in range(3):
            solr_doc_factory(title="test")

        response = client.get(search_url, {"q": "test", "page": "12020"})

        assert response.status_code == HTTPStatus.FOUND
        assert "page=1" in response.url

    def test_valid_page_does_not_redirect(self, client, solr_doc_factory, search_url):
        for _ in range(25):
            solr_doc_factory(title="test")

        response = client.get(search_url, {"q": "test", "page": "2"})

        assert response.status_code == HTTPStatus.OK

    def test_non_integer_page_defaults_to_page_one(self, client, solr_doc_factory, search_url):
        solr_doc_factory(title="test")

        response = client.get(search_url, {"q": "test", "page": "abc"})

        assert response.status_code == HTTPStatus.OK

    def test_negative_page_defaults_to_page_one(self, client, solr_doc_factory, search_url):
        solr_doc_factory(title="test")

        response = client.get(search_url, {"q": "test", "page": "-5"})

        assert response.status_code == HTTPStatus.OK


class TestDatasetView:
    def test_view_existing_dataset_returns_ok(self, client, solr_doc_factory):
        test_uuid = "550e8400-e29b-41d4-a716-446655440000"
        solr_doc_factory(
            id=test_uuid,
            name="test-dataset",
            title="Test Dataset",
            notes="Test notes",
            metadata_modified="2026-01-15T10:00:00Z",
            organization="test-org",
            validated_data_dict=json.dumps(
                {
                    "name": "test-dataset",
                    "id": test_uuid,
                    "organization": {"title": "Test Org"},
                    "resources": [],
                },
            ),
        )

        url = reverse("directory:dataset", kwargs={"uuid": test_uuid, "slug": "test-dataset"})
        response = client.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["doc"].title == "Test Dataset"
        assert response.context_data["doc"].summary == "Test notes"
        assert response.context_data["doc"].organisation["title"] == "Test Org"
        assert response.context_data["doc"].datafiles == []

    def test_view_existing_dataset_organisation_missing_returns_ok(self, client, solr_doc_factory):
        test_uuid = "550e8400-e29b-41d4-a716-446655440000"
        solr_doc_factory(
            id=test_uuid,
            name="test-dataset",
            title="Test Dataset",
            notes="Test notes",
            metadata_modified="2026-01-15T10:00:00Z",
            organization="test-org",
            validated_data_dict=json.dumps(
                {
                    "name": "test-dataset",
                    "id": test_uuid,
                    "organization": {"title": "Test Org"},
                    "resources": [],
                },
            ),
            organisation={"create": False},
        )

        url = reverse("directory:dataset", kwargs={"uuid": test_uuid, "slug": "test-dataset"})
        response = client.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["doc"].title == "Test Dataset"
        assert response.context_data["doc"].summary == "Test notes"
        assert response.context_data["doc"].organisation["title"] == "Test Org"
        assert response.context_data["doc"].datafiles == []

    def test_view_existing_dataset_with_organisation_defaults_returns_ok(self, client, solr_doc_factory):
        test_uuid = "550e8400-e29b-41d4-a716-446655440000"
        solr_doc_factory(
            id=test_uuid,
            name="test-dataset",
            title="Test Dataset",
            notes="Test notes",
            metadata_modified="2026-01-15T10:00:00Z",
            organization="test-org",
            validated_data_dict=json.dumps(
                {
                    "name": "test-dataset",
                    "id": test_uuid,
                    "organization": {"title": "Test Org"},
                    "resources": [],
                },
            ),
            organisation={"extras_foi_web": "https://www.example.net"},
        )

        url = reverse("directory:dataset", kwargs={"uuid": test_uuid, "slug": "test-dataset"})
        response = client.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["doc"].foi_web == "https://www.example.net"

    def test_view_existing_dataset_with_resources(self, client, solr_doc_factory):
        test_uuid = "550e8400-e29b-41d4-a716-446655440001"
        solr_doc_factory(
            id=test_uuid,
            name="dataset-with-resources",
            title="Dataset With Resources",
            notes="Has resources",
            metadata_modified="2026-02-20T15:30:00Z",
            organization="publishing-org",
            validated_data_dict=json.dumps(
                {
                    "name": "dataset-with-resources",
                    "id": test_uuid,
                    "organization": {"title": "Publishing Org"},
                    "resources": [
                        {
                            "id": "770e8400-e29b-41d4-a716-446655440001",
                            "name": "Data file",
                            "url": "http://example.com/data.csv",
                            "format": "CSV",
                            "created": "2026-01-01",
                            "last_modified": None,
                            "size": None,
                        },
                    ],
                },
            ),
        )

        url = reverse("directory:dataset", kwargs={"uuid": test_uuid, "slug": "dataset-with-resources"})
        response = client.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["doc"].title == "Dataset With Resources"
        assert len(response.context_data["doc"].datafiles) == 1
        assert response.context_data["doc"].datafiles[0].name == "Data file"

    def test_view_nonexistent_dataset_returns_404(self, client, solr_doc_factory):
        test_uuid = "00000000-0000-0000-0000-000000000000"
        url = reverse("directory:dataset", kwargs={"uuid": test_uuid, "slug": "nonexistent"})
        response = client.get(url)

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_view_dataset_solr_query_filters_by_id_and_state(self, client, solr_doc_factory):
        test_uuid = "550e8400-e29b-41d4-a716-446655440002"
        solr_doc_factory(
            id=test_uuid,
            name="active-dataset",
            title="Active Dataset",
            notes="Active",
            metadata_modified="2026-03-01T09:00:00Z",
            organization="active-org",
            validated_data_dict=json.dumps(
                {
                    "organization": {"title": "Active Org"},
                    "resources": [],
                },
            ),
        )

        url = reverse("directory:dataset", kwargs={"uuid": test_uuid, "slug": "active-dataset"})
        client.get(url)

    def test_csv_resource_shows_preview_link(self, client, solr_doc_factory):
        test_uuid = "550e8400-e29b-41d4-a716-446655440003"
        resource_uuid = "660e8400-e29b-41d4-a716-446655440003"
        solr_doc_factory(
            id=test_uuid,
            name="csv-dataset",
            title="CSV Dataset",
            notes="Has CSV",
            metadata_modified="2026-01-01T00:00:00Z",
            organization="test-org",
            validated_data_dict=json.dumps(
                {
                    "organization": {"title": "Test Org"},
                    "resources": [
                        {
                            "id": resource_uuid,
                            "name": "Data",
                            "url": "http://example.com/data.csv",
                            "format": "CSV",
                            "created": "2026-01-01",
                            "last_modified": None,
                            "size": None,
                        },
                    ],
                },
            ),
        )

        url = reverse("directory:dataset", kwargs={"uuid": test_uuid, "slug": "csv-dataset"})
        response = client.get(url)

        assert response.context_data["doc"].datafiles[0].is_csv is True
        assert response.context_data["doc"].datafiles[0].url == "http://example.com/data.csv"

    def test_non_csv_resource_shows_not_available(self, client, solr_doc_factory):
        test_uuid = "550e8400-e29b-41d4-a716-446655440004"
        solr_doc_factory(
            id=test_uuid,
            name="xls-dataset",
            title="XLS Dataset",
            notes="Has XLS",
            metadata_modified="2026-01-01T00:00:00Z",
            organization="test-org",
            validated_data_dict=json.dumps(
                {
                    "organization": {"title": "Test Org"},
                    "resources": [
                        {
                            "id": "some-uuid",
                            "name": "Data",
                            "url": "http://example.com/data.xls",
                            "format": "XLS",
                            "created": "2026-01-01",
                            "last_modified": None,
                            "size": None,
                        },
                    ],
                },
            ),
        )

        url = reverse("directory:dataset", kwargs={"uuid": test_uuid, "slug": "xls-dataset"})
        response = client.get(url)

        assert response.context_data["doc"].datafiles[0].is_csv is False

    def test_meta_data_provided(self, client, solr_doc_factory):
        test_uuid = "550e8400-e29b-41d4-a716-446655440005"
        solr_doc_factory(
            id=test_uuid,
            name="dataset-name",
            title="Dataset Title",
            metadata_modified="2026-01-01T00:00:00Z",
            validated_data_dict=json.dumps(
                {
                    "organization": {"title": "Test Org"},
                    "resources": [],
                    "license_title": "Licence title",
                    "license_url": "https://example.com/license",
                },
            ),
        )

        url = reverse("directory:dataset", kwargs={"uuid": test_uuid, "slug": "dataset-name"})
        response = client.get(url)

        assert '<meta name="dc:title" content="Dataset Title"' in response.rendered_content
        assert '<meta name="dc:publisher" content="Test Org"' in response.rendered_content
        assert '<meta name="dc:date" content="2026-01-01"' in response.rendered_content
        assert '<meta name="dc:rights" content="Licence title"' in response.rendered_content

    def test_meta_data_where_license_title_not_provided(self, client, solr_doc_factory):
        test_uuid = "550e8400-e29b-41d4-a716-446655440006"
        solr_doc_factory(
            id=test_uuid,
            name="dataset-name",
            validated_data_dict=json.dumps(
                {
                    "organization": {"title": "Test Org"},
                    "resources": [],
                },
            ),
        )

        url = reverse("directory:dataset", kwargs={"uuid": test_uuid, "slug": "dataset-name"})
        response = client.get(url)

        assert 'name="dc:rights"' not in response.rendered_content
        assert "Not set" in response.rendered_content

    def test_meta_data_where_license_url_not_provided(self, client, solr_doc_factory):
        test_uuid = "550e8400-e29b-41d4-a716-446655440007"
        solr_doc_factory(
            id=test_uuid,
            name="dataset-name",
            validated_data_dict=json.dumps(
                {
                    "organization": {"title": "Test Org"},
                    "resources": [],
                    "license_title": "Licence title",
                },
            ),
        )

        url = reverse("directory:dataset", kwargs={"uuid": test_uuid, "slug": "dataset-name"})
        response = client.get(url)

        assert '<meta name="dc:rights" content="Licence title"' in response.rendered_content
        assert 'rel="dc:rights"' not in response.rendered_content

    def test_meta_data_where_license_title_and_url_not_provided(self, client, solr_doc_factory):
        test_uuid = "550e8400-e29b-41d4-a716-446655440008"
        solr_doc_factory(
            id=test_uuid,
            name="dataset-name",
            validated_data_dict=json.dumps(
                {
                    "organization": {"title": "Test Org"},
                },
            ),
        )

        url = reverse("directory:dataset", kwargs={"uuid": test_uuid, "slug": "dataset-name"})
        response = client.get(url)

        assert 'name="dc:rights"' not in response.rendered_content
        assert 'rel="dc:rights"' not in response.rendered_content
        assert "Not set" in response.rendered_content

    def test_dataset_summary_has_metadata_dc_properties(self, client, solr_doc_factory):
        test_uuid = "550e8400-e29b-41d4-a716-446655440009"
        solr_doc_factory(
            id=test_uuid,
            name="dataset-name",
            metadata_modified="2026-01-01T00:00:00Z",
            validated_data_dict=json.dumps(
                {
                    "organization": {"title": "Test Org"},
                    "license_title": "Licence title",
                    "license_url": "https://example.com/license",
                },
            ),
        )

        url = reverse("directory:dataset", kwargs={"uuid": test_uuid, "slug": "dataset-name"})
        response = client.get(url)

        assert '<span property="dc:publisher">Test Org</span>' in response.rendered_content
        assert '<span property="dc:date">1 January 2026</span>' in response.rendered_content
        assert '<span property="dc:rights">' in response.rendered_content
        assert (
            '<a href="https://example.com/license" class="govuk-link datagovuk-link" rel="dc:rights">Licence title</a>'
            in response.rendered_content
        )
        assert 'property="dc:description"' in response.rendered_content


class TestLegacyDatasetRedirectView:
    def test_legacy_dataset_redirect_view_redirects_to_directory(self, client, solr_doc_factory):
        solr_doc_factory(id="11111111-1111-4111-8111-111111111111", name="some-dataset-name")
        url = reverse("directory:legacy_dataset", kwargs={"legacy_dataset_name": "some-dataset-name"})
        response = client.get(url)
        assert response.status_code == HttpResponsePermanentRedirect.status_code
        assert response.url == reverse(
            "directory:dataset",
            kwargs={"uuid": "11111111-1111-4111-8111-111111111111", "slug": "some-dataset-name"},
        )

    def test_legacy_dataset_redirect_view_returns_404_for_invalid_dataset(self, client, solr_doc_factory):
        solr_doc_factory(id="11111111-1111-4111-8111-111111111112", name="some-other-name")
        url = reverse("directory:legacy_dataset", kwargs={"legacy_dataset_name": "invalid-dataset"})
        response = client.get(url)
        assert response.status_code == HttpResponseNotFound.status_code


class TestLegacyDatafileRedirectView:
    def test_legacy_datafile_redirect_view_redirects_to_preview(self, solr_doc_factory, client):
        solr_doc_factory(
            id="11111111-1111-1111-1111-111111111111",
            name="some-dataset-name",
            validated_data_dict=json.dumps(
                {
                    "resources": [
                        {
                            "id": "22222222-2222-2222-2222-222222222222",
                            "name": "Data",
                            "url": "http://example.com/data.csv",
                            "format": "CSV",
                            "created": "2026-01-01",
                        },
                    ],
                },
            ),
        )
        url = reverse(
            "directory:legacy_datafile",
            kwargs={
                "legacy_dataset_name": "some-dataset-name",
                "datafile_uuid": "22222222-2222-2222-2222-222222222222",
            },
        )
        response = client.get(url)
        assert response.status_code == HttpResponsePermanentRedirect.status_code
        assert response.url == reverse(
            "directory:preview",
            kwargs={
                "dataset_uuid": "11111111-1111-1111-1111-111111111111",
                "name": "some-dataset-name",
                "datafile_uuid": "22222222-2222-2222-2222-222222222222",
            },
        )

    def test_legacy_datafile_redirect_view_returns_404_for_invalid_dataset(
        self,
        solr_doc_factory,
        client,
    ):
        solr_doc_factory(id="11111111-1111-1111-1111-111111111111", name="some-dataset-name")
        url = reverse(
            "directory:legacy_datafile",
            kwargs={
                "legacy_dataset_name": "invalid-dataset",
                "datafile_uuid": "22222222-2222-2222-2222-222222222222",
            },
        )
        response = client.get(url)
        assert response.status_code == HttpResponseNotFound.status_code

    def test_legacy_datafile_redirect_view_returns_404_for_invalid_datafile(
        self,
        solr_doc_factory,
        client,
    ):
        solr_doc_factory(id="11111111-1111-1111-1111-111111111111", name="some-dataset-name")
        unknown_datafile_uuid = "33333333-3333-3333-3333-333333333333"
        url = reverse(
            "directory:legacy_datafile",
            kwargs={
                "legacy_dataset_name": "some-dataset-name",
                "datafile_uuid": unknown_datafile_uuid,
            },
        )
        response = client.get(url)
        assert response.status_code == HttpResponseNotFound.status_code

    @patch("datagovuk.directory.views.reverse", side_effect=NoReverseMatch("NoReverseMatch"))
    def test_legacy_datafile_redirect_view_returns_404_for_no_reverse_match(
        self,
        mock_reverse,
        solr_doc_factory,
        client,
    ):
        solr_doc_factory(
            id="11111111-1111-1111-1111-111111111111",
            name="some-dataset-name",
            validated_data_dict=json.dumps(
                {
                    "resources": [
                        {
                            "id": "22222222-2222-2222-2222-222222222222",
                            "name": "Data",
                            "url": "http://example.com/example.csv",
                            "format": "CSV",
                            "created": "2026-01-01",
                        },
                    ],
                },
            ),
        )
        url = reverse(
            "directory:legacy_datafile",
            kwargs={
                "legacy_dataset_name": "some-dataset-name",
                "datafile_uuid": "22222222-2222-2222-2222-222222222222",
            },
        )
        response = client.get(url)
        assert response.status_code == HttpResponseNotFound.status_code


class TestLegacySearchRedirectView:
    def test_legacy_search_redirect_view_redirects_to_directory_search(self, client):
        url = reverse("directory:legacy_search")
        response = client.get(url)
        assert response.status_code == HttpResponsePermanentRedirect.status_code
        assert response.url == reverse("directory:search")
