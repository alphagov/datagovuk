import json
import uuid
from datetime import UTC, datetime

import pysolr
from django.conf import settings

from .tests.factories import create_solr_doc

DATASET_UUID = "0d94a8d6-a10b-4d6f-9c9e-2a38df9503d1"
DATASET_UUID_NO_EXTRAS = "e6946d44-3090-4e3f-9dd2-4269f0da4f73"
DATASET_SLUG = "test-additional-information-dataset"
DATAFILE_UUID = "9667a107-91ef-424b-be74-f36d35e580d1"


def dataset_with_additional_information(solr_client):
    extras = [
        {"key": "licence", "value": "ogl"},
        {"key": "metadata-date", "value": "2024-06-01T00:00:00"},
        {"key": "guid", "value": "a1b2c3d4-0000-0000-0000-000000000001"},
        {"key": "frequency-of-update", "value": "annual"},
        {"key": "metadata-language", "value": "eng"},
        {"key": "spatial-reference-system", "value": "OSGB 1936 / Test"},
        {"key": "responsible-party", "value": "Example Publisher (pointOfContact)"},
        {"key": "access_constraints", "value": '["Available under the Open Government Licence v3.0"]'},
        {
            "key": "dataset-reference-date",
            "value": json.dumps(
                [{"type": "publication", "value": "2024-01-01"}, {"type": "revision", "value": "2024-06-01"}],
            ),
        },
        {
            "key": "bbox-north-lat",
            "value": "51.686",
        },
        {
            "key": "bbox-south-lat",
            "value": "51.286",
        },
        {
            "key": "bbox-west-long",
            "value": "-0.510",
        },
        {
            "key": "bbox-east-long",
            "value": "-0.489",
        },
        {"key": "metadata-language", "value": "eng"},
        {"key": "resource-type", "value": "dataset"},
        {"key": "harvest_object_id", "value": "harvest-object-abc123"},
    ]
    resources = [
        {
            "id": str(uuid.uuid4()),
            "name": "Resource 1",
            "url": "https://example.com/doc.pdf",
            "format": "PDF",
            "size": None,
            "metadata_modified": datetime.now(UTC).isoformat(),
            "created": datetime.now(UTC).isoformat(),
            "resource-type": "resource",
        },
        {
            "id": DATAFILE_UUID,
            "name": "Resource 2",
            "url": "https://example.com/doc.pdf",
            "format": "CSV",
            "size": None,
            "metadata_modified": datetime.now(UTC).isoformat(),
            "created": datetime.now(UTC).isoformat(),
            "resource-type": "resource",
        },
    ]
    doc = create_solr_doc(
        solr_client,
        id=DATASET_UUID,
        name=DATASET_SLUG,
        title="Test Additional Information Dataset",
        extras=extras,
        resources=resources,
    )
    return doc


def dataset_without_additional_information(solr_client):
    doc = create_solr_doc(
        solr_client,
        id=DATASET_UUID_NO_EXTRAS,
        name=DATASET_SLUG,
        title="Test No Additional Information Dataset",
    )
    return doc


def create_e2e_fixtures():
    client = pysolr.Solr(settings.SOLR_URL, always_commit=True)
    dataset_with_additional_information(client)
    dataset_without_additional_information(client)


def delete_e2e_fixtures():
    client = pysolr.Solr(settings.SOLR_URL, always_commit=True)
    client.delete(q=f"id:{DATASET_UUID} OR id:{DATASET_UUID_NO_EXTRAS}")
