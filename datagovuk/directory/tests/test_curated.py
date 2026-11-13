from pathlib import Path
from unittest.mock import patch

import pytest
from django.conf import settings

from datagovuk.directory.curated import (
    get_all_curated_items,
    get_collection_counts,
    get_curated_items,
    get_suggested_searches,
)


@pytest.fixture(autouse=True)
def clear_curated_cache():
    get_all_curated_items.cache_clear()
    yield
    get_all_curated_items.cache_clear()


def titles(query, topics=(), collections=()):
    return [item.title for item in get_curated_items(query, topics, collections)]


class TestGetAllCuratedItems:
    def test_every_published_collection_page_is_curated_data(self):
        published_pages = list(Path(settings.DATAGOVUK_CONTENT_COLLECTIONS_ROOT).glob("*/*.md"))

        assert len(get_all_curated_items()) == len(published_pages)

    def test_items_have_a_title_summary_and_link_to_their_collection_page(self):
        inflation = next(item for item in get_all_curated_items() if item.title == "Inflation")

        assert inflation.url == "/collections/business-and-economy/inflation"
        assert inflation.summary.startswith("Explore various datasets about inflation and price indices")
        assert "<" not in inflation.summary

    def test_house_prices_is_in_the_business_and_economy_topic_although_filed_under_land_and_property(self):
        house_prices = next(item for item in get_all_curated_items() if item.title == "UK house prices")

        assert house_prices.url == "/collections/land-and-property/uk-house-prices"
        assert house_prices.topic == "Business and economy"

    def test_topics_follow_the_collection_and_pages_in_other_collections_have_none(self):
        topics = {item.title: item.topic for item in get_all_curated_items()}

        assert topics["Air quality"] == "Environment"
        assert topics["Bus statistics"] == "Transport"
        assert topics["Births"] is None

    def test_unpublished_and_missing_pages_are_left_out(self, settings, tmp_path):
        collection_dir = tmp_path / "things"
        collection_dir.mkdir()
        (collection_dir / "live.md").write_text("---\ntitle: Live page\nstatus: for-publication\n---\n\nHello there.\n")
        (collection_dir / "draft.md").write_text("---\ntitle: Draft page\nstatus: draft\n---\n\nNot ready.\n")
        settings.DATAGOVUK_CONTENT_COLLECTIONS_ROOT = f"{tmp_path}/"
        collections = [
            {
                "title": "Things",
                "slug": "things",
                "topics": [
                    {"title": "Live page", "slug": "live"},
                    {"title": "Draft page", "slug": "draft"},
                    {"title": "Missing page", "slug": "missing"},
                ],
            },
        ]

        with patch("datagovuk.directory.curated.get_collections", return_value=collections):
            items = get_all_curated_items()

        assert [item.title for item in items] == ["Live page"]
        assert items[0].summary == "Hello there."
        assert items[0].collection == "Things"


class TestGetCuratedItems:
    def test_inflation_search_finds_the_inflation_page(self):
        assert titles("inflation") == ["Inflation"]

    @pytest.mark.parametrize("query", ["house prices", "Houses", '"house price index"', "UK house price"])
    def test_house_price_searches_show_the_house_prices_item(self, query):
        assert "UK house prices" in titles(query)

    def test_the_best_match_comes_first(self):
        assert titles("house prices")[0] == "UK house prices"

    def test_a_search_can_match_several_items(self):
        assert {"Road noise", "Road safety", "Road traffic", "Road conditions"} <= set(titles("road"))

    def test_plurals_and_longer_forms_match(self):
        assert "Air quality" in titles("air qualities") or "Air quality" in titles("air quality")
        assert "Inflation" in titles("inflationary")

    @pytest.mark.parametrize("query", ["", None, "the of and", "data", "statistics", "xyzzy"])
    def test_unrelated_or_generic_searches_show_nothing(self, query):
        assert get_curated_items(query) == []

    def test_words_shared_with_page_titles_only_by_a_few_letters_do_not_match(self):
        assert "Vocational qualifications" not in titles("air quality")


class TestGetCuratedItemsWithTopics:
    def test_ticking_a_topic_shows_its_items_without_any_search_words(self):
        result = titles("", ["Business and economy"])

        assert {"Inflation", "UK house prices", "UK trade"} <= set(result)
        assert "Air quality" not in result

    def test_ticking_a_topic_still_requires_search_words_to_match_when_there_are_some(self):
        assert titles("inflation", ["Business and economy"]) == ["Inflation"]
        assert titles("xyzzy", ["Business and economy"]) == []

    def test_ticking_another_topic_hides_an_item_even_when_the_search_matches(self):
        assert "UK house prices" not in titles("house prices", ["Environment"])

    def test_items_without_a_topic_match_on_search_words_whatever_topic_is_ticked(self):
        assert titles("births", ["Environment"]) == ["Births"]
        assert titles("", ["Environment"]) == [
            item.title for item in get_all_curated_items() if item.topic == "Environment"
        ]

    def test_several_ticked_topics_include_items_from_each(self):
        result = titles("", ["Environment", "Transport"])

        assert {"Air quality", "Bus statistics"} <= set(result)


class TestGetCuratedItemsWithCollections:
    def test_house_prices_is_filed_under_land_and_property(self):
        house_prices = next(item for item in get_all_curated_items() if item.title == "UK house prices")

        assert house_prices.collection == "Land and property"

    def test_ticking_a_collection_narrows_matches_to_pages_in_it(self):
        assert "UK house prices" in titles("price")
        assert titles("price", collections=["Land and property"]) == ["UK house prices", "Property price paid"]

    def test_ticking_a_collection_shows_all_its_pages_without_any_search_words(self):
        result = titles("", collections=["Transport"])

        assert {"Bus statistics", "Road safety"} <= set(result)
        assert "Inflation" not in result

    def test_ticking_a_collection_still_requires_search_words_to_match_when_there_are_some(self):
        assert titles("inflation", collections=["Business and economy"]) == ["Inflation"]
        assert titles("inflation", collections=["Transport"]) == []

    def test_collections_and_topics_combine(self):
        result = get_curated_items("", ["Environment"], ["Land and property"])

        # Pages in the collection, minus any that belong to a different topic (house prices is Business and economy)
        assert result
        assert {item.collection for item in result} == {"Land and property"}
        assert "UK house prices" not in [item.title for item in result]
        assert "Property price paid" in [item.title for item in result]

    def test_several_ticked_collections_include_pages_from_each(self):
        result = titles("", collections=["Transport", "Environment"])

        assert {"Bus statistics", "Air quality"} <= set(result)


class TestGetCollectionCounts:
    def test_without_search_words_every_page_is_counted_under_its_collection(self):
        counts = get_collection_counts("")

        assert sum(counts.values()) == len(get_all_curated_items())
        assert counts["Transport"] == len([item for item in get_all_curated_items() if item.collection == "Transport"])

    def test_with_search_words_only_matching_pages_are_counted(self):
        counts = get_collection_counts("inflation")

        assert counts["Business and economy"] == 1
        assert sum(counts.values()) == 1

    def test_every_collection_is_listed_even_with_no_pages(self):
        counts = get_collection_counts("xyzzy")

        assert set(counts) == {item.collection for item in get_all_curated_items()}
        assert set(counts.values()) == {0}

    def test_ticked_topics_leave_out_pages_in_other_topics(self):
        counts = get_collection_counts("house price", ["Environment"])

        assert counts["Land and property"] == 1  # Property price paid has no topic; UK house prices is excluded


@pytest.fixture
def no_similar_title_words():
    with patch("datagovuk.directory.curated.get_similar_title_words", return_value=[]) as mock:
        yield mock


@pytest.mark.usefixtures("no_similar_title_words")
class TestGetSuggestedSearches:
    @pytest.mark.parametrize(
        ("query", "suggestion"),
        [("inflaton", "Inflation"), ("Electrisity", "Electricity"), ("enviroment", "Environment")],
    )
    def test_misspelt_words_are_corrected_to_words_the_site_knows(self, query, suggestion):
        assert get_suggested_searches(query)[0] == suggestion

    def test_each_misspelt_word_can_be_corrected(self):
        assert get_suggested_searches("inflaton electrisity")[:2] == ["Inflation", "Electricity"]

    def test_the_same_suggestion_is_only_given_once(self):
        assert get_suggested_searches("inflaton inflatin").count("Inflation") == 1

    def test_words_the_site_already_knows_are_not_suggested_back(self):
        assert "Inflation" not in get_suggested_searches("inflation")

    def test_pages_whose_text_mentions_the_search_words_are_suggested_by_title(self):
        # "ONS" is in the text of these pages but not in any of their titles
        suggestions = get_suggested_searches("ons")

        assert "Inflation" in suggestions
        assert "UK house prices" in suggestions

    def test_pages_already_shown_as_curated_data_are_not_suggested(self):
        assert "Inflation" not in get_suggested_searches("inflation ons")

    def test_best_related_page_comes_first(self):
        suggestions = get_suggested_searches("ons office statistics")

        assert suggestions[0] in {"Inflation", "UK house prices"}

    def test_at_most_three_suggestions_are_given(self):
        assert len(get_suggested_searches("inflaton electrisity enviroment transpot ons")) == 3  # noqa: PLR2004

    @pytest.mark.parametrize("query", ["", None, "the of and", "xyzzy"])
    def test_searches_with_nothing_related_have_no_suggestions(self, query):
        assert get_suggested_searches(query) == []


class TestSuggestionsFromDatasetTitles:
    def test_words_in_dataset_titles_close_to_a_search_word_are_suggested(self):
        with patch("datagovuk.directory.curated.get_similar_title_words", return_value=["fishery"]) as similar:
            suggestions = get_suggested_searches("fishry")

        similar.assert_called_once_with("fishry")
        assert suggestions == ["Fishery"]

    def test_suggestions_from_the_site_vocabulary_come_before_dataset_title_ones_and_page_text_ones(self):
        with patch("datagovuk.directory.curated.get_similar_title_words", return_value=["fishery"]):
            suggestions = get_suggested_searches("inflaton fishry ons")

        assert suggestions[:2] == ["Inflation", "Fishery"]
        assert len(suggestions) == 3  # noqa: PLR2004

    def test_only_the_first_few_unknown_words_are_looked_up(self):
        with patch("datagovuk.directory.curated.get_similar_title_words", return_value=[]) as similar:
            get_suggested_searches("zzaa zzbb zzcc zzdd zzee")

        assert similar.call_count == 3  # noqa: PLR2004
