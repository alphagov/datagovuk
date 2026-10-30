import uuid

import factory


class OrganisationFactory(factory.DictFactory):
    uuid = factory.LazyFunction(lambda: str(uuid.uuid4()))
    slug = factory.Sequence(lambda n: f"organisation-{n}")
    name = factory.LazyAttribute(lambda o: o.slug.replace("-", " ").title())


class DatasetFactory(factory.DictFactory):
    """
    Builds a document for the `datasets` index, as written by the indexer.

    `source` is not part of the `Dataset` model, but it is what OpenSearch filters on to decide
    which search ("ckan" or "collection") a document belongs to.
    """

    uuid = factory.LazyFunction(lambda: str(uuid.uuid4()))
    slug = factory.Sequence(lambda n: f"dataset-{n}")
    title = factory.LazyAttribute(lambda o: o.slug.replace("-", " ").title())
    description_raw = factory.LazyAttribute(lambda o: f"Raw description for {o.title}")
    description = factory.LazyAttribute(lambda o: f"Description for {o.title}")
    organisations = factory.LazyFunction(lambda: [OrganisationFactory()])
    created_at = "2024-01-02T03:04:05+00:00"
    updated_at = "2025-06-07T08:09:10+00:00"
    source = "ckan"
