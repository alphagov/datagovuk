import json
import uuid
from datetime import UTC, datetime

import factory


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
    organization = "e2e-publisher-1"
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

    class Params:
        # These parameters won't appear in the dict output directly
        resources = None
        extras = None
        organization_title = None

    @factory.lazy_attribute
    def validated_data_dict(self):
        # Default organization title based on self.organization if not passed
        org_title = self.organization_title or self.organization.replace("-", " ").title()

        return json.dumps(
            {
                "organization": {"title": org_title},
                "extras": self.extras if self.extras is not None else [],
                "resources": self.resources if self.resources is not None else [],
            },
        )


class SolrOrganisationFactory(factory.DictFactory):
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    site_id = "dgu_organisations"
    name = factory.Sequence(lambda n: f"dataset-{n}")
    title = factory.LazyAttribute(lambda o: o.name.replace("-", " ").title())
    extras_foi_web = ""

    class Meta:
        rename = {
            "extras_foi_web": "extras_foi-web",
        }


def create_solr_doc(solr_client, **kwargs):
    organisation_kwargs = kwargs.pop("organisation", {})
    docs = []
    doc = SolrDocumentFactory(**kwargs)
    docs.append(doc)

    if organisation_kwargs.get("create", True):
        organisation_slug = doc["organization"]
        organisation_name = organisation_slug.replace("-", " ").capitalize()
        organisation_doc = SolrOrganisationFactory(
            title=organisation_name,
            name=organisation_slug,
            **organisation_kwargs,
        )
        docs.append(organisation_doc)

    solr_client.add(docs)
    return doc
