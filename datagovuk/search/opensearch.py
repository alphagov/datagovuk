import json
from datetime import datetime

import boto3
from django.conf import settings
from opensearchpy import AWSV4SignerAuth, OpenSearch, RequestsHttpConnection
from pydantic import BaseModel, Field, model_validator


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
    is_harvested: bool = False
    organisations: list[Organisation] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    additional_information: dict = Field(default_factory=dict)

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
    def harvested(self):
        return self.is_harvested

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
