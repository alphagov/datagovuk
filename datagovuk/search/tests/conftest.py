import importlib

import pytest
from django.urls import clear_url_caches
from opensearchpy import helpers

import config.urls
from datagovuk.search.opensearch import get_opensearch_client


@pytest.fixture
def set_search_v2_flag(settings):
    original_flags = settings.FEATURE_FLAGS_ENABLED

    def _set(enabled):
        settings.FEATURE_FLAGS_ENABLED = ["search-v2"] if enabled else []
        clear_url_caches()
        importlib.reload(config.urls)

    yield _set

    settings.FEATURE_FLAGS_ENABLED = original_flags
    clear_url_caches()
    importlib.reload(config.urls)


@pytest.fixture(autouse=True)
def search_v2_flag_enabled(set_search_v2_flag):
    set_search_v2_flag(enabled=True)


@pytest.fixture(scope="session")
def datasets_index_name(worker_id):
    """
    One index per pytest-xdist worker (`datasets-test-master` when not running in parallel), so that
    tests running concurrently cannot see each other's documents.
    """
    return f"datasets-test-{worker_id}"


@pytest.fixture(scope="session")
def datasets_index(datasets_index_name):
    """
    Creates this worker's index for the test session. The `datasets-*` index template baked into the
    opensearch image supplies the same mapping the indexer uses for real indexes.
    """
    client = get_opensearch_client()
    # Remove any index left behind by an aborted run
    client.indices.delete(index=datasets_index_name, ignore=[404])
    client.indices.create(index=datasets_index_name, body={"settings": {"number_of_replicas": 0}})

    yield datasets_index_name

    client.indices.delete(index=datasets_index_name, ignore=[404])


@pytest.fixture(scope="session")
def collections_index_name(worker_id):
    """
    One index per pytest-xdist worker (`collections-test-master` when not running in parallel), so that
    tests running concurrently cannot see each other's documents.
    """
    return f"collections-test-{worker_id}"


@pytest.fixture(scope="session")
def collections_index(collections_index_name):
    """
    Creates this worker's index for the test session. The `collections-*` index template baked into the
    opensearch image supplies the same mapping the indexer uses for real indexes.
    """
    client = get_opensearch_client()
    # Remove any index left behind by an aborted run
    client.indices.delete(index=collections_index_name, ignore=[404])
    client.indices.create(index=collections_index_name, body={"settings": {"number_of_replicas": 0}})

    yield collections_index_name

    client.indices.delete(index=collections_index_name, ignore=[404])


@pytest.fixture(autouse=True)
def opensearch_client(settings, collections_index, datasets_index):
    """
    Points the search app at this worker's indeces and removes all documents from it before each test.
    """
    settings.OPENSEARCH_DATASETS_INDEX = datasets_index
    settings.OPENSEARCH_COLLECTIONS_INDEX = collections_index
    client = get_opensearch_client()
    for index in [collections_index, datasets_index]:
        client.delete_by_query(
            index=index,
            body={"query": {"match_all": {}}},
            refresh=True,
            conflicts="proceed",
        )
    return client


@pytest.fixture
def opensearch_documents(opensearch_client, datasets_index, collections_index):
    """
    Factory fixture which indexes documents (e.g. built with `DatasetFactory`) and makes them searchable.
    """

    def _load(documents):
        documents_with_index = []
        for document in documents:
            if "collection" in document:
                documents_with_index.append((document, collections_index))
            else:
                documents_with_index.append((document, datasets_index))

        helpers.bulk(
            opensearch_client,
            (
                {"_index": opensearch_index, "_id": document["uuid"], "_source": document}
                for document, opensearch_index in documents_with_index
            ),
            refresh=True,
        )
        return documents

    return _load
