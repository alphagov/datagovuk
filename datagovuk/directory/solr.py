import itertools
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime

import pysolr
from cache_memoize import cache_memoize
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.text import slugify

from .constants import FORMATS, FormatChoices

ORGANISATIONS_LIMIT = 6000

logger = logging.getLogger(__file__)


def get_solr_client():
    if not settings.SOLR_URL:
        message = "SOLR_URL was not set"
        raise ImproperlyConfigured(message)
    return pysolr.Solr(settings.SOLR_URL, always_commit=True, timeout=2)


# TODO: Ideally we would switch to a redis caching backend to cache this once across
#   production app servers.  With in-memory caching, this would cache once per-process
@cache_memoize(10 * 60)
def get_organisations_by_title():
    solr_client = get_solr_client()
    results = solr_client.search(
        q="*:*",
        fq=["site_id:dgu_organisations*"],
        fl=["title", "name"],
        rows=ORGANISATIONS_LIMIT,
    )

    organisations = {doc["title"]: doc["name"] for doc in results}

    return organisations


def _get_query(query):
    # TODO: We should do some escaping to avoid any injection in to our SOLR query
    solr_query = f"(title:({query})^2 OR notes:({query}))"
    if not query:
        solr_query = "*:*"
    return solr_query


def _get_filters(filters=None):
    solr_filters = [
        "state:active",
        "type:dataset",
        "-site_id:dgu_organisations*",
    ]
    if not filters:
        filters = {}

    if filters.get("publisher"):
        all_organisations = get_organisations_by_title()
        organisation_slug = all_organisations.get(filters["publisher"])
        if organisation_slug:
            solr_filters.append(f"organization:{organisation_slug}")

    if filters.get("topic"):
        topic_slug = slugify(filters["topic"])
        solr_filters.append(f"extras_theme-primary:{topic_slug}")

    if filters.get("format"):
        file_format = filters["format"]
        if file_format == FormatChoices.OTHER:
            solr_filters.extend(
                [f'-res_format:"{f}"' for f in list(itertools.chain.from_iterable(FORMATS.values()))],
            )
        elif file_format in FORMATS:
            solr_filters.append(
                " OR ".join(f'res_format:"{f}"' for f in FORMATS[file_format]),
            )

    if filters.get("open_government_licence_only") is True:
        ogl_ids = ("uk-ogl", "OGL-UK-*", "ogl")
        ogl_filter_value = " ".join(ogl_ids)
        solr_filters.append(f"license_id:({ogl_filter_value})")

    return solr_filters


def _get_sort(sort):
    if sort == "recent":
        return "metadata_modified desc"
    return None


def _get_facets():
    return {
        "facet": "true",
        "facet.field": ["organization", "extras_theme-primary", "res_format"],
        "f.organization.facet.limit": ORGANISATIONS_LIMIT,
        "facet.sort": "count",
        "facet.mincount": 1,
    }


def search(query, filters, sort="best", start=0, rows=20):
    solr_query = _get_query(query)
    solr_filters = _get_filters(filters)
    solr_client = get_solr_client()
    solr_facets = _get_facets()
    solr_sort = _get_sort(sort)
    search_options = {
        **solr_facets,
    }
    if solr_sort:
        search_options["sort"] = solr_sort
    solr_results = solr_client.search(
        q=solr_query,
        fq=solr_filters,
        start=start,
        rows=rows,
        **search_options,
    )
    docs = [SolrDataset.from_solr_doc(result) for result in solr_results]
    return {
        "results": solr_results,
        "docs": docs,
    }


def get_document(document_id):
    solr_client = get_solr_client()
    solr_results = solr_client.search(
        q=f"id:{document_id}",
        fq=_get_filters(),
    )
    if solr_results.hits == 0:
        return None
    docs = [SolrDataset.from_solr_doc(result) for result in solr_results]
    return docs[0]


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
    last_modified: datetime
    created: str
    size: str
    is_csv: bool = False
    _preview: Preview | None = field(default=None, repr=False)

    @staticmethod
    def from_resource(resource: dict, dataset_created_at: str):
        resource_format = resource.get("format") or ""
        resource_format = resource_format.strip().removeprefix(".").removesuffix(".").upper()

        last_modified = resource.get("last_modified")
        if last_modified:
            last_modified = datetime.fromisoformat(last_modified)

        return SolrDatafile(
            name=resource.get("name") or resource.get("description") or "",
            url=resource.get("url", ""),
            created_at=resource.get("created") or dataset_created_at,
            format=resource_format,
            uuid=resource.get("id", ""),
            is_csv=resource_format == "CSV",
            last_modified=last_modified,
            created=resource.get("created", ""),
            size=resource.get("size", ""),
        )

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
    public_updated_at: datetime
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

    @staticmethod
    def from_solr_doc(doc: dict):
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
        public_updated_at = None
        metadata_modified = doc.get("metadata_modified")
        if metadata_modified:
            public_updated_at = datetime.fromisoformat(metadata_modified)

        return SolrDataset(
            uuid=doc.get("id", ""),
            name=doc.get("name", ""),
            title=doc.get("title", ""),
            summary=doc.get("notes", ""),
            organisation_name=doc.get("organization", ""),
            organisation=dataset_dict.get("organization", ""),
            public_updated_at=public_updated_at,
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
