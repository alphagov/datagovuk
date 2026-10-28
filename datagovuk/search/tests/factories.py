import uuid

import factory


class OrganisationFactory(factory.DictFactory):
    uuid = factory.LazyFunction(lambda: str(uuid.uuid4()))
    slug = factory.Sequence(lambda n: f"organisation-{n}")
    name = factory.LazyAttribute(lambda o: o.slug.replace("-", " ").title())


class DatasetFactory(factory.DictFactory):
    """
    Builds a document for the `datasets` index.
    """

    uuid = factory.LazyFunction(lambda: str(uuid.uuid4()))
    slug = factory.Sequence(lambda n: f"dataset-{n}")
    title = factory.LazyAttribute(lambda o: o.slug.replace("-", " ").title())
    description_raw = factory.LazyAttribute(lambda o: f"Raw description for {o.title}")
    description = factory.LazyAttribute(lambda o: f"Description for {o.title}")
    organisations = factory.LazyFunction(lambda: [OrganisationFactory()])
    created_at = "2024-01-02T03:04:05+00:00"
    updated_at = "2025-06-07T08:09:10+00:00"


class CollectionFactory(factory.DictFactory):
    """
    Builds a document for the `collections` index.
    """

    uuid = factory.LazyFunction(lambda: str(uuid.uuid4()))
    slug = factory.Sequence(lambda n: f"collection-topic-{n}")
    collection = factory.Sequence(lambda n: f"collection-{n}")
    title = factory.LazyAttribute(lambda o: o.slug.replace("-", " ").title())
    description_raw = factory.LazyAttribute(lambda o: f"Raw description for {o.title}")
    description = factory.LazyAttribute(lambda o: f"Description for {o.title}")
    organisations = factory.LazyFunction(lambda: [OrganisationFactory()])
    created_at = "2024-01-02T03:04:05+00:00"
    updated_at = "2025-06-07T08:09:10+00:00"
