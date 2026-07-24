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
    res_format = []

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
