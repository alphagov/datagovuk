import json
from dataclasses import dataclass
from datetime import datetime

import boto3
from django.conf import settings
from opensearchpy import AWSV4SignerAuth, OpenSearch, Q, RequestsHttpConnection, Search
from opensearchpy.helpers.faceted_search import Facet, FacetedResponse, FacetedSearch, NestedFacet, TermsFacet
from opensearchpy.helpers.query import Terms
from pydantic import BaseModel, Field, model_validator

from .constants import FormatChoices


class Organisation(BaseModel):
    uuid: str
    slug: str
    name: str


class Resource(BaseModel):
    uuid: str
    name: str | None = None
    description: str | None = None
    format: str | None = None
    url: str
    resource_type: str | None = None
    size: int | None = None
    created_at: datetime | None = None
    last_modified: datetime | None = None

    @model_validator(mode="before")
    @classmethod
    def default_name(cls, data):
        if not data.get("name"):
            if data.get("resource_type") == "supporting-document":
                data["name"] = "No name specified"
            else:
                data["name"] = data.get("description")
        return data

    @property
    def file_size(self):
        return self.size

    @property
    def last_updated(self):
        return self.last_modified or self.created_at

    @property
    def is_csv(self):
        return self.format == "CSV"


class Dataset(BaseModel):
    uuid: str
    slug: str
    title: str
    description_raw: str
    description: str
    is_harvested: bool = False
    organisations: list[Organisation] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    additional_information: dict = Field(default_factory=dict)
    resources: list[Resource] = Field(default_factory=list)

    @property
    def name(self):
        return self.slug

    @property
    def datafiles(self):
        return [resource for resource in self.resources if resource.resource_type != "supporting-document"]

    @property
    def docs(self):
        return [resource for resource in self.resources if resource.resource_type == "supporting-document"]

    @model_validator(mode="before")
    @classmethod
    def convert_additional_information(cls, data):
        result = {}
        for info in data.get("additional_information", []):
            key = info.get("key")
            value = info.get("value")
            value_type = info.get("type")
            if key is not None:
                if value_type == "json":
                    try:
                        result[key] = json.loads(value)
                    except json.JSONDecodeError, TypeError:
                        result[key] = value
                elif key == "metadata-date":
                    try:
                        result[key] = datetime.fromisoformat(value) if value else None
                    except ValueError:
                        result[key] = None
                else:
                    result[key] = value
        data["additional_information"] = result
        return data

    @property
    def organisation(self):
        return self.organisations[0]


class Collection(BaseModel):
    uuid: str
    slug: str
    collection: str | None = None
    title: str
    description_raw: str
    description: str
    organisations: list[Organisation] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class SearchResult:
    response: dict
    docs: list

    @property
    def total(self):
        return self.response["hits"]["total"]["value"]


@dataclass(frozen=True)
class DirectorySearchResult(SearchResult):
    facets: dict


def get_aws_sigv4_auth():
    session = boto3.Session()
    credentials = session.get_credentials()
    region = settings.AWS_REGION
    return AWSV4SignerAuth(credentials, region)


def get_opensearch_client():
    return OpenSearch(
        hosts=[settings.OPENSEARCH_URL],
        use_ssl=settings.AWS_OPENSEARCH_USE_SSL,
        verify_certs=settings.AWS_OPENSEARCH_VERIFY_CERTS,
        connection_class=RequestsHttpConnection,
        http_auth=get_aws_sigv4_auth(),
    )


def search_collections(query):
    client = get_opensearch_client()
    if query and query.strip():
        search_clause = {
            "multi_match": {
                "query": query,
                "fields": [
                    "title^3",  # High relevance for exact/standard title matches
                    "title.english^2",  # Medium relevance for stemmed English title matches
                ],
                "type": "best_fields",
            },
        }
    else:
        search_clause = {"match_all": {}}

    response = client.search(
        index=settings.OPENSEARCH_COLLECTIONS_INDEX,
        body={
            "query": {
                "bool": {
                    "must": [search_clause],
                },
            },
            "size": 2,
        },
    )
    documents = [Collection(**hit["_source"]) for hit in response["hits"]["hits"]]
    return SearchResult(response=response, docs=documents)


class MultiTermsFacet(Facet):
    """
    Facet over several fields at once (e.g. a slug and its display label), filtered on the first field only.
    """

    agg_type = "multi_terms"

    def __init__(self, fields, **kwargs):
        self._fields = fields
        super().__init__(terms=[{"field": field} for field in fields], **kwargs)

    def add_filter(self, filter_values):
        slug_field = self._fields[0]
        return Terms(**{slug_field: filter_values})

    def get_value(self, bucket):
        return tuple(bucket["key"])

    def is_filtered(self, key, filter_values):
        return key[0] in filter_values


class ReverseNestedTermsFacet(TermsFacet):
    """
    Terms facet for use inside a `NestedFacet` which counts parent documents rather than nested ones.

    This is for e.g. resources where we have a nested opensearch document; for the format facet,
    we don't want the count of the nested documents (resources) - instead we want the count of
    matching parent documents (datasets).
    """

    def get_aggregation(self):
        agg = super().get_aggregation()
        agg.bucket("parent_docs", "reverse_nested")
        # Buckets default to ordering by nested doc count, which isn't the count we show
        agg.order = {"parent_docs": "desc"}
        return agg

    def get_metric(self, bucket):
        return bucket["parent_docs"]["doc_count"]


class BooleanFilterFacet(Facet):
    """
    Facet with a single "on" value, which counts and filters by documents matching `query`.
    """

    agg_type = "filters"

    def __init__(self, query, **kwargs):
        self._query = query
        super().__init__(filters={"on": query}, **kwargs)

    def add_filter(self, filter_values):
        return self._query

    def get_values(self, data, filter_values):
        return [("on", data["buckets"]["on"]["doc_count"], bool(filter_values))]


class DirectorySearch(FacetedSearch):
    facets = {
        "topic": MultiTermsFacet(fields=["topic_slug", "topic.keyword"], size=10000),
        "publisher": MultiTermsFacet(fields=["organisations.slug", "organisations.name.keyword"], size=10000),
        "format": NestedFacet("resources", ReverseNestedTermsFacet(field="resources.format", size=10000)),
        "open_government_licence_only": BooleanFilterFacet(Q("term", licence__slug="uk-ogl")),
    }

    def search(self):
        search = Search(using=get_opensearch_client(), index=settings.OPENSEARCH_DATASETS_INDEX)
        return search.response_class(FacetedResponse).extra(size=20)

    def query(self, search, query):
        if query and query.strip():
            return search.query(
                "multi_match",
                query=query,
                fields=[
                    "title^3",  # High relevance for exact/standard title matches
                    "title.english^2",  # Medium relevance for stemmed English title matches
                    "description",
                    "description.english",
                ],
                type="best_fields",
            )
        return search


def _get_directory_facets(response):
    facets = response.facets
    return {
        "topic": [{"value": value, "label": label, "count": count} for (value, label), count, _ in facets.topic],
        "publisher": [
            {"value": value, "label": label, "count": count} for (value, label), count, _ in facets.publisher
        ],
        "format": [
            {"value": value, "label": value, "count": count}
            for value, count, _ in facets.format
            if value and value.upper() in FormatChoices.values
        ],
        "open_government_licence_only": [
            {"value": value, "label": "Open Government Licence", "count": count}
            for value, count, _ in facets.open_government_licence_only
        ],
    }


def search_directory(query, filters=None):
    facet_filters = {name: value for name, value in (filters or {}).items() if name in DirectorySearch.facets and value}
    response = DirectorySearch(query, filters=facet_filters).execute()
    raw_response = response.to_dict()
    documents = [Dataset(**hit["_source"]) for hit in raw_response["hits"]["hits"]]
    return DirectorySearchResult(response=raw_response, docs=documents, facets=_get_directory_facets(response))


def get_directory_document_by_slug(slug):
    client = get_opensearch_client()

    query_body = {
        "query": {
            "bool": {
                "filter": [
                    {"term": {"slug": slug}},
                ],
            },
        },
        "size": 1,
    }

    response = client.search(index=settings.OPENSEARCH_DATASETS_INDEX, body=query_body)

    hits = response["hits"]["hits"]
    if not hits:
        return None  # Document not found

    source_data = hits[0]["_source"]

    return Dataset(**source_data)
