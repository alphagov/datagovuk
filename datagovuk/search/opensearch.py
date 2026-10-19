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
