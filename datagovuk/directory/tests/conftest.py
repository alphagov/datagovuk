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
    license_id = ""
    topic = ""

    class Meta:
        rename = {
            "topic": "extras_theme-primary",
        }


class SolrOrganisationFactory(SolrDocumentFactory):
    site_id = "dgu_organisations"


@pytest.fixture
def solr_doc_factory(solr_client):

    def _create(**kwargs):
        doc = SolrDocumentFactory(**kwargs)

        organisation_slug = doc["organization"]
        organisation_name = organisation_slug.replace("-", " ").capitalize()
        organisation_doc = SolrOrganisationFactory(title=organisation_name, name=organisation_slug)

        solr_client.add([doc, organisation_doc])
        return doc

    return _create


@pytest.fixture
def sample_solr_docs(solr_doc_factory):
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
        organization="regular-publisher-2",
    )
    doc_3 = solr_doc_factory(
        id="aa8a5b2c-8382-43f7-9f97-dee406c896c4",
        name="excluded-dataset",
        title="Excluded Dataset",
        notes="multi",
        organization="dgu_organisations_123",
        site_id="dgu_organisations_123",
    )
    doc_4 = solr_doc_factory(
        id="66c40d9c-bd29-42a9-9461-cd10d4898664",
        name="other-dataset-3",
        title="Other Dataset 3",
        license_id="ogl",
        organization="regular-publisher-2",
    )
    doc_5 = solr_doc_factory(
        id="66c40d9c-bd29-42a9-9461-cd10d4898664",
        name="other-dataset-4",
        title="Other Dataset 4",
        topic="some-topic",
        organization="regular-publisher-2",
    )
    return [doc_1, doc_2, doc_3, doc_4, doc_5]
