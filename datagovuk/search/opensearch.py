from datetime import datetime  # noqa: TC003

from django.conf import settings
from opensearchpy import OpenSearch
from pydantic import BaseModel, Field


class Organisation(BaseModel):
    uuid: str
    slug: str
    name: str


class Dataset(BaseModel):
    uuid: str
    slug: str
    collection: str | None = None
    title: str
    description_raw: str
    description: str
    organisations: list[Organisation] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    @property
    def organisation(self):
        return self.organisations[0]


def get_opensearch_client():
    # TODO: Switching off SSL/cert verification as this works for local copies only
    #   We will need something more sophisticated for real AWS environments
    return OpenSearch(
        hosts=[settings.OPENSEARCH_URL],
        use_ssl=False,
        verify_certs=False,
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
        index="datasets",
        body={
            "query": {
                "bool": {
                    "must": [search_clause],
                    "filter": [
                        {"term": {"source": "collection"}},
                    ],
                },
            },
            "size": 2,
        },
    )
    documents = [Dataset(**hit["_source"]) for hit in response["hits"]["hits"]]
    return response, documents


def search_directory(query):
    client = get_opensearch_client()
    if query and query.strip():
        search_clause = {
            "multi_match": {
                "query": query,
                "fields": [
                    "title^3",  # High relevance for exact/standard title matches
                    "title.english^2",  # Medium relevance for stemmed English title matches
                    "description",
                    "description.english",
                ],
                "type": "best_fields",
            },
        }
    else:
        search_clause = {"match_all": {}}

    response = client.search(
        index="datasets",
        body={
            "query": {
                "bool": {
                    "must": [search_clause],
                    "filter": [
                        {"term": {"source": "ckan"}},
                    ],
                },
            },
            "size": 20,
        },
    )
    documents = [Dataset(**hit["_source"]) for hit in response["hits"]["hits"]]
    return response, documents


def get_directory_document_by_slug(slug):
    client = get_opensearch_client()

    query_body = {
        "query": {
            "bool": {
                "filter": [
                    {"term": {"slug": slug}},
                    {"term": {"source": "ckan"}},
                ],
            },
        },
        "size": 1,
    }

    response = client.search(index="datasets", body=query_body)

    hits = response["hits"]["hits"]
    if not hits:
        return None  # Document not found

    source_data = hits[0]["_source"]

    return Dataset(**source_data)
