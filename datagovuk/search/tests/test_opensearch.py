import uuid

import pytest
from pydantic import ValidationError

from datagovuk.search.opensearch import (
    Dataset,
    get_directory_document_by_slug,
    get_opensearch_client,
    search_collections,
    search_directory,
)

from .factories import DatasetFactory

COLLECTION_RESULTS = 2
DIRECTORY_RESULTS = 20
EXTRA_RESULTS = 3


def _slugs(documents):
    return [document.slug for document in documents]


def test_get_opensearch_client_connects_to_configured_cluster():
    client = get_opensearch_client()

    assert client.ping() is True


def test_search_collections_matches_on_title(opensearch_documents):
    opensearch_documents(
        [
            DatasetFactory(source="collection", slug="in-title", title="Rail timetables"),
            DatasetFactory(source="collection", slug="other", title="Bus routes"),
        ],
    )

    _, results = search_collections("rail")

    assert _slugs(results) == ["in-title"]


def test_search_collections_does_not_match_on_description(opensearch_documents):
    opensearch_documents(
        [DatasetFactory(source="collection", title="Bus routes", description="Includes rail replacement services")],
    )

    _, results = search_collections("rail")

    assert results == []


def test_search_collections_matches_stemmed_title(opensearch_documents):
    opensearch_documents([DatasetFactory(source="collection", slug="railway", title="Railway stations")])

    _, results = search_collections("railways")

    assert _slugs(results) == ["railway"]


def test_search_collections_with_padded_query_matches(opensearch_documents):
    opensearch_documents([DatasetFactory(source="collection", slug="rail", title="Rail timetables")])

    _, results = search_collections("  rail  ")

    assert _slugs(results) == ["rail"]


@pytest.mark.parametrize("query", [None, "", " ", " \t\n "])
def test_search_collections_with_blank_query_matches_all(query, opensearch_documents):
    opensearch_documents(
        [
            DatasetFactory(source="collection", slug="first", title="Rail timetables"),
            DatasetFactory(source="collection", slug="second", title="Bus routes"),
        ],
    )

    _, results = search_collections(query)

    assert sorted(_slugs(results)) == ["first", "second"]


def test_search_collections_returns_raw_response_and_documents_in_hit_order(opensearch_documents):
    opensearch_documents([DatasetFactory(source="collection", title=f"Rail collection {i}") for i in range(2)])

    response, results = search_collections("rail")

    assert all(isinstance(result, Dataset) for result in results)
    assert _slugs(results) == [hit["_source"]["slug"] for hit in response["hits"]["hits"]]
    assert len(results) == len(response["hits"]["hits"])


def test_search_collections_without_hits_returns_no_documents(opensearch_documents):
    opensearch_documents([DatasetFactory(source="collection", title="Rail timetables")])

    response, results = search_collections("nothing matches")

    assert response["hits"]["total"]["value"] == 0
    assert results == []


def test_search_collections_with_invalid_document_raises(opensearch_documents):
    opensearch_documents([{"uuid": str(uuid.uuid4()), "slug": "rail", "title": "Rail", "source": "collection"}])

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

    assert _slugs(results) == ["from-collection"]


def test_search_collections_limits_documents_but_not_total(opensearch_documents):
    opensearch_documents([DatasetFactory(source="collection") for _ in range(COLLECTION_RESULTS + EXTRA_RESULTS)])

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
    opensearch_documents([{"uuid": str(uuid.uuid4()), "slug": "rail", "title": "Rail", "source": "ckan"}])

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

    assert _slugs(results) == ["from-ckan"]


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


def test_get_directory_document_by_slug_requires_exact_match(opensearch_documents):
    opensearch_documents([DatasetFactory(slug="wanted-dataset")])

    assert get_directory_document_by_slug("wanted") is None


def test_get_directory_document_by_slug_ignores_collection_document_with_same_slug(opensearch_documents):
    opensearch_documents([DatasetFactory(slug="wanted", source="collection")])

    assert get_directory_document_by_slug("wanted") is None


def test_get_directory_document_by_slug_with_invalid_document_raises(opensearch_documents):
    opensearch_documents([{"uuid": str(uuid.uuid4()), "slug": "wanted", "source": "ckan"}])

    with pytest.raises(ValidationError):
        get_directory_document_by_slug("wanted")
