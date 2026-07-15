import json
from dataclasses import dataclass, field


@dataclass
class Preview:
    url: str
    format: str
    exists: bool = False


@dataclass
class SolrDatafile:
    name: str
    url: str
    created_at: str
    format: str
    uuid: str
    is_csv: bool = False
    _preview: Preview | None = field(default=None, repr=False)

    @classmethod
    def from_resource(cls, resource: dict, dataset_created_at: str):
        resource_format = resource.get("format") or ""
        resource_format = resource_format.strip().removeprefix(".").removesuffix(".").upper()
        return SolrDatafile(
            name=resource.get("name") or resource.get("description") or "",
            url=resource.get("url", ""),
            created_at=resource.get("created") or dataset_created_at,
            format=resource_format,
            uuid=resource.get("id", ""),
            is_csv=resource_format == "CSV",
        )

    # Lazily create a Preview object for the datafile
    def get_preview(self):
        if self._preview is None:
            self._preview = Preview(url=self.url, format=self.format)
        return self._preview

    @property
    def preview(self):
        return self.get_preview()

    class DatafileNotFoundError(Exception):
        pass


@dataclass
class SolrDataset:
    uuid: str
    name: str
    title: str
    summary: str
    public_updated_at: str
    topic: str
    licence_title: str
    licence_url: str
    datafiles: list = field(default_factory=list)
    contact_email: str = ""
    contact_name: str = ""
    foi_name: str = ""
    foi_email: str = ""
    foi_web: str = ""
    docs: list = field(default_factory=list)
    licence_custom: str = ""
    inspire_dataset: bool = False
    harvested: bool = False
    licence_code: str = ""
    organisation: dict = field(default_factory=dict)
    organisation_name: str = ""
    is_organogram: bool = False

    @classmethod
    def from_solr_doc(cls, doc: dict):
        dataset_dict = json.loads(doc.get("validated_data_dict", "{}"))
        dataset_created_at = doc.get("metadata_created", "")

        datafiles = []
        docs = []
        for resource in dataset_dict.get("resources", []):
            if resource.get("resource-type") == "supporting-document":
                docs.append(resource)
            else:
                datafiles.append(SolrDatafile.from_resource(resource, dataset_created_at))

        topic = doc.get("extras_theme-primary", "") or ""
        if topic:
            topic = topic.replace("-", " ").capitalize()

        licence_custom = doc.get("extras_licence", "") or ""
        if licence_custom:
            licence_custom = licence_custom.replace('"', "").replace("[", "").replace("]", "")

        return SolrDataset(
            uuid=doc.get("id", ""),
            name=doc.get("name", ""),
            title=doc.get("title", ""),
            summary=doc.get("notes", ""),
            public_updated_at=doc.get("metadata_modified", ""),
            topic=topic,
            licence_title=dataset_dict.get("license_title", ""),
            licence_url=dataset_dict.get("license_url", ""),
            licence_code=dataset_dict.get("license_id", ""),
            licence_custom=licence_custom,
            contact_email=dataset_dict.get("contact-email", ""),
            contact_name=dataset_dict.get("contact-name", ""),
            foi_name=dataset_dict.get("foi-name", ""),
            foi_email=dataset_dict.get("foi-email", ""),
            foi_web=dataset_dict.get("foi-web", ""),
            datafiles=datafiles,
            docs=docs,
        )
