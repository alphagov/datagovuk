from datetime import datetime  # noqa: TC003

import boto3
from django.conf import settings
from opensearchpy import AWSV4SignerAuth, OpenSearch, RequestsHttpConnection
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
        index=settings.OPENSEARCH_DATASETS_INDEX,
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
        index=settings.OPENSEARCH_DATASETS_INDEX,
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

    response = client.search(index=settings.OPENSEARCH_DATASETS_INDEX, body=query_body)

    hits = response["hits"]["hits"]
    if not hits:
        return None  # Document not found

    source_data = hits[0]["_source"]

    return Dataset(**source_data)
