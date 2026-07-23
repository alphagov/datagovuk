import uuid
from datetime import UTC, datetime

import factory
import pysolr
import pytest


@pytest.fixture
def solr_url(settings):
    return settings.SOLR_URL + "-test"


@pytest.fixture(autouse=True)
def override_solr_settings(solr_url, settings):
    """
    Overrides Django settings for all tests to point to the temporary container.
    """
    settings.SOLR_URL = solr_url
    settings.FEATURE_FLAGS_ENABLED = [settings.FEATURE_FLAGS.SOLR_SEARCH.value]


@pytest.fixture
def solr_client(solr_url):
    """
    pysolr Client connected to the container.
    Wipes all Solr data before and after each test for test isolation.
    """
    client = pysolr.Solr(solr_url, always_commit=True)

    client.delete(q="*:*")
    yield client
    client.delete(q="*:*")


class SolrDocumentFactory(factory.DictFactory):
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"dataset-{n}")
    title = factory.LazyAttribute(lambda o: o.name.replace("-", " ").title())
    notes = factory.LazyAttribute(lambda o: f"Description for {o.title}")
    metadata_created = factory.LazyFunction(
        lambda: datetime.now(UTC).isoformat(),
    )
    metadata_modified = factory.LazyAttribute(lambda o: o.metadata_created)
    state = "active"
    organization = "example-publisher-1"
    capacity = "public"
    entity_type = "package"
    dataset_type = "dataset"
    type = "dataset"
    site_id = "default"


@pytest.fixture
def solr_doc_factory(solr_client):
    """
    Factory fixture that generates documents using SolrDocumentFactory
    and indexes them directly into the test Solr container.
    """

    def _create(**kwargs):
        doc = SolrDocumentFactory(**kwargs)

        solr_client.add([doc])
        return doc

    return _create


@pytest.fixture
def sample_solr_docs(solr_doc_factory):
    """Populates Solr with a set of default documents for standard tests."""
    doc_1 = solr_doc_factory(
        id="66c40d9c-bd29-42a9-9461-cd10d4898662",
        name="test-dataset",
        title="Test Dataset",
        notes="multi",
        organization="regular-publisher",
    )
    doc_2 = solr_doc_factory(
        id="66c40d9c-bd29-42a9-9461-cd10d4898663",
        name="other-dataset-2",
        title="Other Dataset 2",
        notes="multi",
        organization="regular-publisher",
    )
    doc_3 = solr_doc_factory(
        id="aa8a5b2c-8382-43f7-9f97-dee406c896c4",
        name="excluded-dataset",
        title="Excluded Dataset",
        notes="multi",
        organization="dgu_organisations_123",
        site_id="dgu_organisations_123",
    )
    return [doc_1, doc_2, doc_3]
