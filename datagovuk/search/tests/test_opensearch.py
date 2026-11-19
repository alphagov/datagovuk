import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

from datagovuk.search.opensearch import (
    Collection,
    Dataset,
    Resource,
    get_directory_document_by_slug,
    get_opensearch_client,
    search_collections,
    search_directory,
)

from .factories import CollectionFactory, DatasetFactory, ResourceFactory

COLLECTION_RESULTS = 2
DIRECTORY_RESULTS = 20
EXTRA_RESULTS = 3


def _slugs(documents):
    return [document.slug for document in documents]


def test_resource_last_updated_falls_back_to_created_at_when_no_last_modified():
    resource = Resource(**ResourceFactory(last_modified=None, created_at="2026-06-01T00:00:00+00:00"))
    assert resource.last_updated == datetime.fromisoformat("2026-06-01T00:00:00+00:00")


def test_resource_last_updated_prefers_last_modified_when_multiple_dates_present():
    resource = Resource(
        **ResourceFactory(
            last_modified="2026-01-01T00:00:00+00:00",
            created_at="2023-01-01T00:00:00+00:00",
        ),
    )
    assert resource.last_updated == datetime.fromisoformat("2026-01-01T00:00:00+00:00")


def test_resource_last_updated_returns_none_when_all_dates_absent():
    resource = Resource(**ResourceFactory(last_modified=None, created_at=None))
    assert resource.last_updated is None


def test_resource_supporting_document_name_defaults_to_no_name_specified():
    resource = Resource(**ResourceFactory(name=None, resource_type="supporting-document"))
    assert resource.name == "No name specified"


def test_resource_name_defaults_to_description_when_not_supporting_document():
    resource = Resource(**ResourceFactory(name=None, description="My description", resource_type="data-link"))
    assert resource.name == "My description"


def test_resource_name_is_none_when_no_name_or_description():
    resource = Resource(**ResourceFactory(name=None, resource_type="data-link"))
    assert resource.name is None


def test_resource_name_is_kept_when_present():
    resource = Resource(**ResourceFactory(name="My file", description="My description", resource_type="data-link"))
    assert resource.name == "My file"


def test_resource_is_csv_true_for_csv_format():
    assert Resource(**ResourceFactory(format="CSV")).is_csv is True


def test_resource_is_csv_false_for_non_csv_format():
    assert Resource(**ResourceFactory(format="JSON")).is_csv is False


def test_resource_is_csv_false_when_format_is_none():
    assert Resource(**ResourceFactory(format=None)).is_csv is False


def test_dataset_additional_information_list_converted_to_dict():
    dataset = DatasetFactory(additional_information=[{"key": "licence", "value": "test", "type": "string"}])
    assert Dataset(**dataset).additional_information == {"licence": "test"}


def test_dataset_additional_information_json_value_key_is_parsed():
    additional_information = [
        {"key": "access_constraints", "value": '["OGL"]', "type": "json"},
        {"key": "dataset-reference-date", "value": '[{"type": "creation", "value": "2026-01-01"}]', "type": "json"},
    ]
    dataset = DatasetFactory(additional_information=additional_information)
    assert Dataset(**dataset).additional_information == {
        "access_constraints": ["OGL"],
        "dataset-reference-date": [{"type": "creation", "value": "2026-01-01"}],
    }


def test_dataset_additional_information_invalid_json_falls_back_to_raw_string():
    dataset = DatasetFactory(
        additional_information=[{"key": "access_constraints", "value": "invalid-json", "type": "json"}],
    )
    assert Dataset(**dataset).additional_information == {"access_constraints": "invalid-json"}


def test_dataset_additional_information_none_value_falls_back_to_none():
    dataset = DatasetFactory(additional_information=[{"key": "access_constraints", "value": None, "type": "json"}])
    assert Dataset(**dataset).additional_information == {"access_constraints": None}


def test_dataset_additional_information_without_key_is_skipped():
    dataset = DatasetFactory(
        additional_information=[
            {"key": None, "value": "ignored", "type": "json"},
            {"key": "test-key", "value": "test-value", "type": "string"},
        ],
    )
    assert Dataset(**dataset).additional_information == {"test-key": "test-value"}


def test_dataset_additional_information_empty_list_produces_empty_dict():
    dataset = DatasetFactory(additional_information=[])
    assert Dataset(**dataset).additional_information == {}


def test_dataset_additional_information_defaults_to_empty_dict():
    dataset = DatasetFactory()
    del dataset["additional_information"]
    assert Dataset(**dataset).additional_information == {}


def test_dataset_is_harvested_true():
    dataset = DatasetFactory(is_harvested=True)
    assert Dataset(**dataset).is_harvested is True


def test_dataset_is_harvested_false():
    dataset = DatasetFactory(is_harvested=False)
    assert Dataset(**dataset).is_harvested is False


def test_dataset_is_harvested_defaults_to_false():
    dataset = DatasetFactory()
    del dataset["is_harvested"]
    assert Dataset(**dataset).is_harvested is False


def test_dataset_additional_information_metadata_date_is_parsed():
    dataset = DatasetFactory(
        additional_information=[{"key": "metadata-date", "value": "2026-03-04T05:06:07", "type": "string"}],
    )
    assert Dataset(**dataset).additional_information == {
        "metadata-date": datetime.fromisoformat("2026-03-04T05:06:07"),
    }


def test_dataset_additional_information_invalid_metadata_date_is_none():
    dataset = DatasetFactory(
        additional_information=[{"key": "metadata-date", "value": "not-a-date", "type": "string"}],
    )
    assert Dataset(**dataset).additional_information == {"metadata-date": None}


def test_dataset_additional_information_empty_metadata_date_is_none():
    dataset = DatasetFactory(additional_information=[{"key": "metadata-date", "value": None, "type": "string"}])
    assert Dataset(**dataset).additional_information == {"metadata-date": None}


def test_get_opensearch_client_connects_to_configured_cluster():
    client = get_opensearch_client()

    assert client.ping() is True


def test_search_collections_matches_on_title(opensearch_documents):
    opensearch_documents(
        [
            CollectionFactory(slug="in-title", title="Rail timetables"),
            CollectionFactory(slug="other", title="Bus routes"),
        ],
    )

    _, results = search_collections("rail")
    assert _slugs(results) == ["in-title"]


def test_search_collections_does_not_match_on_description(opensearch_documents):
    opensearch_documents(
        [CollectionFactory(title="Bus routes", description="Includes rail replacement services")],
    )

    _, results = search_collections("rail")

    assert results == []


def test_search_collections_matches_stemmed_title(opensearch_documents):
    opensearch_documents([CollectionFactory(slug="railway", title="Railway stations")])

    _, results = search_collections("railways")

    assert _slugs(results) == ["railway"]


def test_search_collections_with_padded_query_matches(opensearch_documents):
    opensearch_documents([CollectionFactory(slug="rail", title="Rail timetables")])

    _, results = search_collections("  rail  ")

    assert _slugs(results) == ["rail"]


@pytest.mark.parametrize("query", [None, "", " ", " \t\n "])
def test_search_collections_with_blank_query_matches_all(query, opensearch_documents):
    opensearch_documents(
        [
            CollectionFactory(slug="first", title="Rail timetables"),
            CollectionFactory(slug="second", title="Bus routes"),
        ],
    )

    _, results = search_collections(query)

    assert sorted(_slugs(results)) == ["first", "second"]


def test_search_collections_returns_raw_response_and_documents_in_hit_order(opensearch_documents):
    opensearch_documents([CollectionFactory(title=f"Rail collection {i}") for i in range(2)])

    response, results = search_collections("rail")

    assert all(isinstance(result, Collection) for result in results)
    assert _slugs(results) == [hit["_source"]["slug"] for hit in response["hits"]["hits"]]
    assert len(results) == len(response["hits"]["hits"])


def test_search_collections_without_hits_returns_no_documents(opensearch_documents):
    opensearch_documents([CollectionFactory(title="Rail timetables")])

    response, results = search_collections("nothing matches")

    assert response["hits"]["total"]["value"] == 0
    assert results == []


def test_search_collections_with_invalid_document_raises(opensearch_documents):
    opensearch_documents([{"uuid": str(uuid.uuid4()), "collection": "foo", "title": "Rail"}])

    with pytest.raises(ValidationError):
        search_collections("rail")


def test_search_collections_only_returns_collection_documents(opensearch_documents):
    opensearch_documents(
        [
            DatasetFactory(slug="from-ckan"),
            CollectionFactory(slug="from-collection"),
        ],
    )

    _, results = search_collections("")

    assert _slugs(results) == ["from-collection"]


def test_search_collections_limits_documents_but_not_total(opensearch_documents):
    opensearch_documents([CollectionFactory() for _ in range(COLLECTION_RESULTS + EXTRA_RESULTS)])

    response, results = search_collections("")

    assert len(results) == COLLECTION_RESULTS
    assert response["hits"]["total"]["value"] == COLLECTION_RESULTS + EXTRA_RESULTS


def test_search_directory_matches_on_title_and_description(opensearch_documents):
    opensearch_documents(
        [
            DatasetFactory(slug="in-title", title="Rail timetables"),
            DatasetFactory(slug="in-description", title="Bus routes", description="Includes rail replacement"),
            DatasetFactory(slug="other", title="Road traffic", description="Counts of vehicles"),
        ],
    )

    _, results = search_directory("rail")

    assert sorted(_slugs(results)) == ["in-description", "in-title"]


def test_search_directory_ranks_title_matches_above_description_matches(opensearch_documents):
    opensearch_documents(
        [
            DatasetFactory(slug="in-description", title="Bus routes", description="Includes rail replacement"),
            DatasetFactory(slug="in-title", title="Rail timetables", description="Timetables for trains"),
        ],
    )

    _, results = search_directory("rail")

    assert _slugs(results) == ["in-title", "in-description"]


def test_search_directory_matches_stemmed_title_and_description(opensearch_documents):
    opensearch_documents(
        [
            DatasetFactory(slug="in-title", title="Railway stations"),
            DatasetFactory(slug="in-description", title="Bus routes", description="Replacement railway services"),
        ],
    )

    _, results = search_directory("railways")

    assert sorted(_slugs(results)) == ["in-description", "in-title"]


def test_search_directory_with_padded_query_matches(opensearch_documents):
    opensearch_documents([DatasetFactory(slug="rail", title="Rail timetables")])

    _, results = search_directory("  rail  ")

    assert _slugs(results) == ["rail"]


@pytest.mark.parametrize("query", [None, "", " ", " \t\n "])
def test_search_directory_with_blank_query_matches_all(query, opensearch_documents):
    opensearch_documents(
        [
            DatasetFactory(slug="first", title="Rail timetables"),
            DatasetFactory(slug="second", title="Bus routes"),
        ],
    )

    _, results = search_directory(query)

    assert sorted(_slugs(results)) == ["first", "second"]


def test_search_directory_returns_raw_response_and_documents_in_hit_order(opensearch_documents):
    opensearch_documents([DatasetFactory(title=f"Rail dataset {i}") for i in range(2)])

    response, results = search_directory("rail")

    assert all(isinstance(result, Dataset) for result in results)
    assert _slugs(results) == [hit["_source"]["slug"] for hit in response["hits"]["hits"]]
    assert len(results) == len(response["hits"]["hits"])


def test_search_directory_without_hits_returns_no_documents(opensearch_documents):
    opensearch_documents([DatasetFactory(title="Rail timetables")])

    response, results = search_directory("nothing matches")

    assert response["hits"]["total"]["value"] == 0
    assert results == []


def test_search_directory_with_invalid_document_raises(opensearch_documents):
    opensearch_documents([{"uuid": str(uuid.uuid4()), "slug": "rail", "title": "Rail"}])

    with pytest.raises(ValidationError):
        search_directory("rail")


def test_search_directory_only_returns_ckan_documents(opensearch_documents):
    opensearch_documents(
        [
            DatasetFactory(slug="from-ckan"),
            CollectionFactory(slug="from-collection"),
        ],
    )

    _, results = search_directory("")

    assert _slugs(results) == ["from-ckan"]


def test_search_directory_limits_documents_but_not_total(opensearch_documents):
    opensearch_documents([DatasetFactory() for _ in range(DIRECTORY_RESULTS + EXTRA_RESULTS)])

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


def test_get_directory_document_by_slug_requires_exact_match(opensearch_documents):
    opensearch_documents([DatasetFactory(slug="wanted-dataset")])

    assert get_directory_document_by_slug("wanted") is None


def test_get_directory_document_by_slug_ignores_collection_document_with_same_slug(opensearch_documents):
    opensearch_documents([CollectionFactory(slug="wanted")])

    assert get_directory_document_by_slug("wanted") is None


def test_get_directory_document_by_slug_with_invalid_document_raises(opensearch_documents):
    opensearch_documents([{"uuid": str(uuid.uuid4()), "slug": "wanted"}])

    with pytest.raises(ValidationError):
        get_directory_document_by_slug("wanted")
