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
    return OpenSearch(
        hosts=[settings.OPENSEARCH_URL],
        use_ssl=False,
        verify_certs=False,
    )


def search(query):
    client = get_opensearch_client()
    response = client.search(
        index="datasets",
        body={
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["title.english^2", "description.english"],
                            },
                        },
                    ],
                },
            },
        },
    )
    documents = [Dataset(**hit["_source"]) for hit in response["hits"]["hits"]]
    return response, documents


def get_document_by_slug(slug):
    client = get_opensearch_client()

    query_body = {"query": {"term": {"slug": slug}}, "size": 1}

    response = client.search(index="datasets", body=query_body)

    hits = response["hits"]["hits"]
    if not hits:
        return None  # Document not found

    source_data = hits[0]["_source"]

    return Dataset(**source_data)
