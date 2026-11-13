import json
import re
from http import HTTPStatus
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlsplit

import pytest
from django.http import HttpResponseNotFound, HttpResponsePermanentRedirect
from django.urls import NoReverseMatch, reverse

from datagovuk.directory.constants import TopicChoices
from datagovuk.directory.curated import CuratedItem
from datagovuk.directory.views import SearchView

CURATED_ITEMS_SHOWN_FIRST = 2
EVERY_TOPIC = sorted(topic for topic in TopicChoices.values if topic)


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

    def test_view_filter_include_datasets_with_no_links(self, client, solr_doc_factory, search_url):
        matching_doc = solr_doc_factory()
        doc_missing_links = solr_doc_factory(res_url=[])

        response = client.get(search_url, {"q": "dataset"})

        assert response.status_code == HTTPStatus.OK
        expected_ids = [matching_doc["id"]]
        actual_ids = [doc["id"] for doc in response.context_data["results"].docs]
        assert actual_ids == expected_ids

        response = client.get(search_url, {"q": "dataset", "include_datasets_with_no_links": "on"})

        assert response.status_code == HTTPStatus.OK
        expected_ids = [matching_doc["id"], doc_missing_links["id"]]
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

    def test_search_view_facets_ignore_their_own_filter_but_reduce_with_the_others(
        self,
        client,
        solr_doc_factory,
        search_url,
    ):
        doc_1 = solr_doc_factory(name="test", organization="some-other-publisher")
        doc_2 = solr_doc_factory(name="test", organization="my-publisher")
        doc_3 = solr_doc_factory(name="test", organization="my-publisher", topic="Environment")
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

        def doc_ids(response):
            return [doc["id"] for doc in response.context_data["results"].docs]

        def options(response, field):
            return sorted(value for value, _ in response.context_data["form"].fields[field].choices)

        def topic_counts(response):
            return {topic: count for topic, count in response.context_data["facet_counts"]["topic"].items() if count}

        query = "test"
        # Firstly search for all 'test' records...
        response = client.get(search_url, {"q": query})
        assert doc_ids(response) == [doc_1["id"], doc_2["id"], doc_3["id"], doc_4["id"], doc_5["id"], doc_6["id"]]
        assert options(response, "publisher") == ["My publisher", "Some other publisher"]
        assert options(response, "topic") == ["Business and economy", "Environment"]
        assert topic_counts(response) == {"Environment": 3, "Business and economy": 1}
        assert options(response, "format") == ["CSV", "JSON", "XLS"]

        # Filtering by publisher reduces the other groups, but publishers stay available to tick as well...
        response = client.get(search_url, {"q": query, "publisher": "My publisher"})
        assert doc_ids(response) == [doc_2["id"], doc_3["id"], doc_4["id"], doc_5["id"], doc_6["id"]]
        assert options(response, "publisher") == ["My publisher", "Some other publisher"]
        assert options(response, "topic") == ["Business and economy", "Environment"]
        assert topic_counts(response) == {"Environment": 3, "Business and economy": 1}
        assert options(response, "format") == ["CSV", "JSON", "XLS"]

        # Next filter by publisher and topic...
        response = client.get(search_url, {"q": query, "publisher": "My publisher", "topic": "Environment"})
        assert doc_ids(response) == [doc_3["id"], doc_5["id"], doc_6["id"]]
        assert options(response, "publisher") == ["My publisher"]
        assert options(response, "topic") == ["Business and economy", "Environment"]
        assert topic_counts(response) == {"Environment": 3, "Business and economy": 1}
        assert options(response, "format") == ["CSV", "JSON", "XLS"]

        # Next filter by publisher, topic and format...
        response = client.get(
            search_url,
            {"q": query, "publisher": "My publisher", "topic": "Environment", "format": "XLS"},
        )
        assert doc_ids(response) == [doc_6["id"]]
        assert options(response, "publisher") == ["My publisher"]
        assert options(response, "topic") == ["Environment"]
        assert topic_counts(response) == {"Environment": 1}
        assert options(response, "format") == ["CSV", "JSON", "XLS"]

    def test_search_view_multiple_selected_values_in_a_group_are_or_d(self, client, solr_doc_factory, search_url):
        environment = solr_doc_factory(name="test", topic="Environment", res_format=["CSV"])
        business = solr_doc_factory(name="test", topic="Business and economy", res_format=["JSON"])
        solr_doc_factory(name="test", topic="Transport", res_format=["XLS"])

        response = client.get(search_url + "?q=test&topic=Environment&topic=Business+and+economy")
        assert {doc["id"] for doc in response.context_data["results"].docs} == {environment["id"], business["id"]}

        response = client.get(search_url + "?q=test&format=CSV&format=JSON")
        assert {doc["id"] for doc in response.context_data["results"].docs} == {environment["id"], business["id"]}

        response = client.get(search_url + "?q=test&topic=Environment&topic=Business+and+economy&format=JSON")
        assert [doc["id"] for doc in response.context_data["results"].docs] == [business["id"]]

    def test_search_view_provides_facet_counts_even_without_a_query(self, client, solr_doc_factory, search_url):
        solr_doc_factory(name="one", topic="Environment", res_format=["CSV"])
        solr_doc_factory(name="two", topic="Environment", res_format=["JSON"])

        response = client.get(search_url, {"query": ""})

        assert response.context_data["facet_counts"]["topic"] == {**dict.fromkeys(EVERY_TOPIC, 0), "Environment": 2}
        assert response.context_data["facet_counts"]["format"] == {"CSV": 1, "JSON": 1}

    def test_search_view_shows_curated_data_only_when_the_search_is_related(self, client, solr_doc_factory, search_url):
        solr_doc_factory(name="inflation", title="Inflation data")
        solr_doc_factory(name="other", title="Something else")

        related = client.get(search_url, {"query": "inflation"})
        unrelated = client.get(search_url, {"query": "something"})

        assert [item.title for item in related.context_data["curated_items"]] == ["Inflation"]
        assert "Curated data" in related.content.decode()
        assert unrelated.context_data["curated_items"] == []
        assert "Curated data" not in unrelated.content.decode()

    def test_search_view_shows_curated_data_even_when_there_are_no_datasets(self, client, search_url):
        response = client.get(search_url, {"query": "air quality"})

        content = response.content.decode()
        assert response.context_data["results"].hits == 0
        assert "/collections/environment/air-quality" in content
        assert "No results found" not in content
        assert "This may be because" not in content

    def test_search_view_says_no_results_found_when_nothing_matches_at_all(self, client, search_url):
        response = client.get(search_url, {"query": "Quantum Farming Subsidies"})

        content = response.content.decode()
        assert response.context_data["curated_items"] == []
        assert "No results found" in content
        assert "No datasets match your search for \u2018Quantum Farming Subsidies\u2019." in content
        assert "the National Data Library does not have data on this topic" in content
        assert "using fewer or broader search terms" in content
        assert "browsing by topic filters" in content

    def test_search_view_no_results_message_escapes_what_was_searched_for(self, client, search_url):
        response = client.get(search_url, {"query": "<script>alert(1)</script>"})

        content = response.content.decode()
        assert "<script>alert(1)</script>" not in content
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in content

    def test_search_view_no_results_message_for_filters_without_a_search(self, client, search_url):
        response = client.get(search_url, {"query": "", "topic": "Health"})

        content = response.content.decode()
        assert "No results found" in content
        assert "No datasets match the filters you have chosen." in content

    def test_search_view_suggests_a_correction_for_a_misspelt_search(self, client, search_url):
        response = client.get(search_url, {"query": "inflaton"})

        assert response.context_data["suggested_searches"][0] == "Inflation"
        content = response.content.decode()
        assert "No results found" in content
        assert "Suggested searches" in content
        assert 'href="/search?query=Inflation"' in content
        assert ">Inflation</a>" in content

    def test_search_view_suggests_pages_related_to_what_was_searched_for(self, client, search_url):
        response = client.get(search_url, {"query": "ons"})

        suggestions = response.context_data["suggested_searches"]
        assert "UK house prices" in suggestions
        assert 'href="/search?query=UK%20house%20prices"' in response.content.decode()

    def test_search_view_has_no_suggested_searches_when_there_are_results_or_nothing_is_close(
        self,
        client,
        solr_doc_factory,
        search_url,
    ):
        solr_doc_factory(name="inflaton", title="Inflaton data")

        with_results = client.get(search_url, {"query": "inflaton"})
        nothing_close = client.get(search_url, {"query": "quantum farming subsidies"})

        for response in (with_results, nothing_close):
            assert response.context_data["suggested_searches"] == []
            assert "Suggested searches" not in response.content.decode()

    def test_search_view_shows_the_feedback_strip_when_nothing_is_found(self, client, search_url):
        response = client.get(search_url, {"query": "xyzzy"})

        assert "Is this data/dataset useful?" in response.content.decode()

    def test_search_view_curated_data_follows_the_topic_filter(self, client, solr_doc_factory, search_url):
        solr_doc_factory(name="house", topic="Environment")

        in_topic = client.get(search_url, {"query": "", "topic": "Business and economy"})
        search_in_topic = client.get(search_url, {"query": "house", "topic": "Business and economy"})
        other_topic = client.get(search_url, {"query": "house", "topic": "Environment"})

        assert "Inflation" in [item.title for item in in_topic.context_data["curated_items"]]
        assert "UK house prices" in [item.title for item in search_in_topic.context_data["curated_items"]]
        assert "UK house prices" not in [item.title for item in other_topic.context_data["curated_items"]]

    def test_search_view_shows_file_formats_in_sentence_case(self, client, solr_doc_factory, search_url):
        resources = [
            {"url": f"https://example.com/{file_format}", "format": file_format}
            for file_format in ("CSV", "xlsx", "Pdf")
        ]
        solr_doc_factory(name="cases", resources=resources)

        response = client.get(search_url, {"query": "cases"})

        content = response.content.decode()
        for expected in (">Csv</li>", ">Xlsx</li>", ">Pdf</li>"):
            assert expected in content.replace("\n", "").replace("  ", ""), expected
        assert ">CSV</li>" not in content
        assert "text-transform" not in content

    def test_search_view_gives_every_file_format_an_icon(self, client, solr_doc_factory, search_url):
        formats_per_dataset = [
            ["CSV", "XLSX", "PDF", "JSON"],
            ["HTML", "ZIP", "SHP", "API"],
            ["MP3", "AVI", "PNG", "FOOBAR"],
        ]
        for formats in formats_per_dataset:
            resources = [
                {"url": f"https://example.com/{file_format}", "format": file_format} for file_format in formats
            ]
            solr_doc_factory(name="formats", resources=resources)

        response = client.get(search_url, {"query": "formats"})

        content = response.content.decode()
        for icon in (
            "table",
            "file-spreadsheet",
            "file-text",
            "file-json",
            "file-code",
            "file-archive",
            "map",
            "globe",
            "file-audio",
            "file-video",
            "image",
            "file",
        ):
            assert f'datagovuk-format-icon--{icon}"' in content, icon

    def test_search_view_has_a_filter_by_button_that_controls_the_filters_panel(self, client, search_url):
        content = client.get(search_url, {"query": "inflation"}).content.decode()

        assert "data-filter-toggle" in content
        assert 'aria-controls="search-filters"' in content
        assert 'id="search-filters"' in content

    def test_search_view_curated_data_info_icon_explains_who_chose_the_pages(self, client, search_url):
        content = client.get(search_url, {"query": "inflation"}).content.decode()

        assert 'role="tooltip"' in content
        assert "Selected by the National Data Library team" in content
        assert 'aria-describedby="curated-info"' in content
        assert 'id="curated-info"' in content
        # the old browser-only tooltip is gone
        assert "Hand-picked guidance" not in content

    def test_search_view_curated_data_shows_two_items_then_a_show_more_button_for_the_rest(
        self,
        client,
        search_url,
    ):
        items = [
            CuratedItem(title=f"Item {number}", summary="Summary", url=f"/item-{number}", keywords=("x",))
            for number in range(1, 5)
        ]
        with patch("datagovuk.directory.views.get_curated_items", return_value=items):
            response = client.get(search_url, {"query": "anything"})

        content = response.content.decode()
        assert "data-more-toggle" in content
        main_part, _, extra_part = content.partition('id="curated-more-options"')
        assert "Item 1" in main_part
        assert "Item 2" in main_part
        assert "Item 3" not in main_part
        assert "Item 3" in extra_part
        assert "Item 4" in extra_part

    def test_search_view_curated_data_has_no_show_more_button_for_two_items_or_fewer(self, client, search_url):
        response = client.get(search_url, {"query": "inflation"})

        assert len(response.context_data["curated_items"]) == 1
        assert 'id="curated-more-options"' not in response.content.decode()

    def test_search_view_curated_data_shows_a_show_more_button_when_many_pages_match(self, client, search_url):
        response = client.get(search_url, {"query": "road"})

        assert len(response.context_data["curated_items"]) > CURATED_ITEMS_SHOWN_FIRST
        assert 'id="curated-more-options"' in response.content.decode()

    def test_search_view_collection_filter_comes_first_and_topic_second(self, client, solr_doc_factory, search_url):
        solr_doc_factory(name="one")

        response = client.get(search_url, {"query": ""})

        content = response.content.decode()
        titles_in_order = re.findall(r'datagovuk-filter-group__title">([A-Za-z]+)<', content)
        assert titles_in_order[:2] == ["Collection", "Topic"]

    def test_search_view_offers_only_collections_that_have_pages_for_the_search(self, client, search_url):
        response = client.get(search_url, {"query": "inflation"})

        choices = response.context_data["form"].fields["collection"].choices
        assert choices == [("Business and economy", "Business and economy")]
        assert response.context_data["collection_counts"]["Business and economy"] == 1
        content = response.content.decode()
        assert re.search(r'Business and economy\s*<span class="datagovuk-choice__count">\(1\)</span>', content)

    def test_search_view_with_no_search_words_offers_every_collection_with_its_page_count(self, client, search_url):
        response = client.get(search_url, {"query": ""})

        choices = [value for value, _ in response.context_data["form"].fields["collection"].choices]
        counts = response.context_data["collection_counts"]
        assert sorted(choices) == sorted(counts)
        assert all(counts[collection] for collection in choices)
        assert choices[0] == max(counts, key=counts.get)

    def test_search_view_ticking_a_collection_narrows_curated_data_but_not_datasets(
        self,
        client,
        solr_doc_factory,
        search_url,
    ):
        solr_doc_factory(name="price", title="Price paid")

        everything = client.get(search_url, {"query": "price"})
        in_collection = client.get(search_url, {"query": "price", "collection": "Land and property"})
        other_collection = client.get(search_url, {"query": "price", "collection": "Transport"})

        assert len(in_collection.context_data["curated_items"]) < len(everything.context_data["curated_items"])
        assert {item.collection for item in in_collection.context_data["curated_items"]} == {"Land and property"}
        assert other_collection.context_data["curated_items"] == []
        for response in (everything, in_collection, other_collection):
            assert response.context_data["results"].hits == 1

    def test_search_view_ticked_collection_shows_as_a_chip_before_other_filters(self, client, search_url):
        response = client.get(
            search_url,
            {"query": "price", "topic": "Business and economy", "collection": "Land and property"},
        )

        assert [chip["label"] for chip in response.context_data["active_filters"]] == [
            "Land and property",
            "Business and economy",
        ]

    def test_search_view_shows_curated_data_on_the_first_page_only(self, client, solr_doc_factory, search_url):
        for _ in range(25):
            solr_doc_factory(title="house")

        first_page = client.get(search_url, {"query": "house"})
        second_page = client.get(search_url, {"query": "house", "page": "2"})

        assert "Curated data" in first_page.content.decode()
        assert "Curated data" not in second_page.content.decode()

    def test_topic_choices_list_every_topic_when_browsing_with_the_most_results_first(self):
        choices = SearchView.get_topic_choices({"Transport": 5, "Environment": 9}, include_empty=True)

        values = [value for value, _ in choices]
        assert sorted(values) == EVERY_TOPIC
        assert values[:2] == ["Environment", "Transport"]

    def test_topic_choices_list_only_topics_with_results_when_searching(self):
        choices = SearchView.get_topic_choices({"Transport": 5, "Environment": 9, "Health": 0}, include_empty=False)

        assert [value for value, _ in choices] == ["Environment", "Transport"]

    def test_search_view_with_no_search_words_offers_every_topic(self, client, solr_doc_factory, search_url):
        solr_doc_factory(name="one", topic="Environment")

        response = client.get(search_url, {"query": ""})

        topic_options = [value for value, _ in response.context_data["form"].fields["topic"].choices]
        assert sorted(topic_options) == EVERY_TOPIC
        assert topic_options[0] == "Environment"

    def test_search_view_with_search_words_only_offers_topics_that_have_results(
        self,
        client,
        solr_doc_factory,
        search_url,
    ):
        solr_doc_factory(name="one", topic="Environment")

        response = client.get(search_url, {"query": "one"})

        assert [value for value, _ in response.context_data["form"].fields["topic"].choices] == ["Environment"]

    def test_search_view_offers_no_topic_format_or_publisher_options_when_nothing_is_found(self, client, search_url):
        response = client.get(search_url, {"query": "xyzzy"})

        form = response.context_data["form"]
        assert form.fields["topic"].choices == []
        assert form.fields["format"].choices == []
        assert form.fields["publisher"].choices == []
        content = response.content.decode()
        assert 'name="topic"' not in content
        assert 'name="format"' not in content
        assert 'name="publisher"' not in content

    def test_search_view_keeps_only_the_ticked_options_when_filters_leave_nothing(
        self,
        client,
        solr_doc_factory,
        search_url,
    ):
        solr_doc_factory(name="one", topic="Environment", res_format=["CSV"])

        response = client.get(search_url, {"query": "one", "topic": "Business and economy"})

        form = response.context_data["form"]
        assert form.fields["topic"].choices == [("Business and economy", "Business and economy")]
        assert form.fields["format"].choices == []

    def test_search_view_keeps_ticked_options_that_are_missing_from_the_facets(self):
        choices = {
            "collection_choices": [],
            "publisher_choices": [("My publisher", "My publisher")],
            "topic_choices": [("Environment", "Environment")],
            "format_choices": [],
        }
        filters = {
            "collection": ["Transport"],
            "publisher": ["My publisher"],
            "topic": ["Environment", "Transport"],
            "format": ["CSV"],
        }

        result = SearchView.with_selected(choices, filters)

        assert result == {
            "collection_choices": [("Transport", "Transport")],
            "publisher_choices": [("My publisher", "My publisher")],
            "topic_choices": [("Environment", "Environment"), ("Transport", "Transport")],
            "format_choices": [("CSV", "CSV")],
        }

    def test_search_view_active_filters_list_each_ticked_filter_with_a_link_that_removes_it(
        self,
        client,
        solr_doc_factory,
        search_url,
    ):
        solr_doc_factory(name="test", topic="Environment", res_format=["CSV", "JSON"], license_id="uk-ogl")

        response = client.get(
            search_url
            + "?q=test&topic=Environment&format=CSV&format=JSON&open_government_licence_only=on"
            + "&include_datasets_with_no_links=on&sort=recent&page=1",
        )

        chips = response.context_data["active_filters"]
        assert [chip["label"] for chip in chips] == [
            "Environment",
            "CSV",
            "JSON",
            "Open Government Licence (OGL) only",
            "Include datasets with no links",
        ]
        remove_csv = parse_qs(urlsplit(chips[1]["remove_url"]).query)
        assert remove_csv["format"] == ["JSON"]
        assert remove_csv["topic"] == ["Environment"]
        assert remove_csv["sort"] == ["recent"]
        assert "page" not in remove_csv
        remove_licence = parse_qs(urlsplit(chips[3]["remove_url"]).query)
        assert "open_government_licence_only" not in remove_licence
        assert remove_licence["include_datasets_with_no_links"] == ["on"]

        clear_all = parse_qs(urlsplit(response.context_data["clear_filters_url"]).query)
        assert clear_all == {"q": ["test"], "query": ["test"], "sort": ["recent"]}

        content = response.content.decode()
        assert "datagovuk-filter-chip" in content
        assert "Clear all" in content

    def test_search_view_shows_no_active_filters_when_none_are_ticked(self, client, solr_doc_factory, search_url):
        solr_doc_factory(name="test")

        response = client.get(search_url, {"q": "test"})

        assert response.context_data["active_filters"] == []
        assert "datagovuk-filter-chip" not in response.content.decode()

    def test_search_view_other_format_combined_with_a_named_format(self, client, solr_doc_factory, search_url):
        other = solr_doc_factory(name="test", res_format=["woop"])
        csv = solr_doc_factory(name="test", res_format=["CSV"])
        solr_doc_factory(name="test", res_format=["XLS"])

        response = client.get(search_url + "?q=test&format=OTHER&format=CSV")

        assert {doc["id"] for doc in response.context_data["results"].docs} == {other["id"], csv["id"]}

    def test_search_view_provides_facet_counts_for_topic_and_format(self, client, solr_doc_factory, search_url):
        solr_doc_factory(name="test", topic="Environment", res_format=["CSV", ".csv"])
        solr_doc_factory(name="test", topic="Environment", res_format=["CSV", "woop"])
        solr_doc_factory(name="test", topic="Business and economy", res_format=["JSON"])

        response = client.get(search_url, {"q": "test"})

        assert response.context_data["facet_counts"] == {
            "publisher": {"E2e publisher 1": 3},
            "topic": {**dict.fromkeys(EVERY_TOPIC, 0), "Environment": 2, "Business and economy": 1},
            "format": {"CSV": 2, "OTHER": 1, "JSON": 1},
        }
        content = response.content.decode()
        assert re.search(r"Environment\s*<span class=\"datagovuk-choice__count\">\(2\)</span>", content)
        assert re.search(r"CSV\s*<span class=\"datagovuk-choice__count\">\(2\)</span>", content)

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

    def test_view_existing_dataset_with_no_resources(self, client, solr_doc_factory):
        test_uuid = "550e8400-e29b-41d4-a716-446655440001"
        solr_doc_factory(
            id=test_uuid,
            name="dataset-with-resources",
            title="Dataset With Resources",
            notes="Has resources",
            metadata_modified="2026-02-20T15:30:00Z",
            organization="publishing-org",
            res_url=[],
            validated_data_dict=json.dumps(
                {
                    "name": "dataset-with-resources",
                    "id": test_uuid,
                    "organization": {"title": "Publishing Org"},
                },
            ),
        )

        url = reverse("directory:dataset", kwargs={"uuid": test_uuid, "slug": "dataset-with-resources"})
        response = client.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["doc"].title == "Dataset With Resources"
        assert len(response.context_data["doc"].datafiles) == 0

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
            '<a href="https://example.com/license" class="datagovuk-dataset__link datagovuk-dataset__link--plain" '
            'rel="dc:rights">Licence title</a>'
        ) in response.rendered_content
        assert 'property="dc:description"' in response.rendered_content


class TestDatasetPageDesign:
    @staticmethod
    def get_page(client, solr_doc_factory, **overrides):
        test_uuid = overrides.pop("id", "550e8400-e29b-41d4-a716-446655440100")
        solr_doc_factory(id=test_uuid, name="dataset-name", title="Housing valuations", **overrides)
        url = reverse("directory:dataset", kwargs={"uuid": test_uuid, "slug": "dataset-name"})
        return client.get(url)

    def test_shows_the_new_header_with_search_and_not_the_directory_band(self, client, solr_doc_factory):
        response = self.get_page(client, solr_doc_factory)

        content = response.rendered_content
        assert 'placeholder="Search"' in content
        assert "datagovuk-directory-header" not in content

    def test_metadata_uses_the_designed_labels(self, client, solr_doc_factory):
        content = self.get_page(client, solr_doc_factory, topic="Environment").rendered_content

        for label in ("Published by:", "Last updated:", "Topic:", "Licence:"):
            assert label in content
        assert "Environment" in content

    def test_data_links_table_has_last_update_column_na_for_no_preview_and_day_month_year_dates(
        self,
        client,
        solr_doc_factory,
    ):
        resources = [
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "name": "A file",
                "url": "http://example.com/a.pdf",
                "format": "PDF",
                "last_modified": "2024-06-24T10:00:00",
                "created": "2024-06-24T10:00:00",
            },
        ]
        content = self.get_page(client, solr_doc_factory, resources=resources).rendered_content

        assert "Last update" in content
        assert "N/A" in content
        assert "24/06/2024" in content

    def test_contact_uses_the_designed_wording(self, client, solr_doc_factory):
        content = self.get_page(
            client,
            solr_doc_factory,
            validated_data_dict=json.dumps(
                {
                    "organization": {"title": "Test Org"},
                    "contact-email": "enquiries@example.org",
                    "foi-email": "foi@example.org",
                    "foi-web": "https://example.org/foi",
                },
            ),
        ).rendered_content

        assert "Enquiries" in content
        assert 'href="mailto:enquiries@example.org"' in content
        assert "Freedom of Information (FOI) requests" in content
        assert 'href="mailto:foi@example.org"' in content
        assert "Freedom of information requests for this dataset" in content

    def test_edit_section_points_to_the_data_manual(self, client, solr_doc_factory):
        content = self.get_page(client, solr_doc_factory).rendered_content

        assert "Edit this dataset" in content
        assert re.search(r'href="/data-manual[^"]*"[^>]*>\s*Data manual', content)
        assert "Sign in" not in content

    def test_more_from_this_publisher_links_to_that_publishers_datasets(self, client, solr_doc_factory):
        content = self.get_page(client, solr_doc_factory, organization="my-publisher").rendered_content

        assert "More from this publisher" in content
        assert 'href="/search?publisher=My%20Publisher"' in content


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
