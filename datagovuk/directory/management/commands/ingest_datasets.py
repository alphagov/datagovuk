import json
import uuid
from datetime import UTC, datetime

import pysolr
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from datagovuk.directory.tests.factories import create_solr_doc


class Command(BaseCommand):
    help = "Create solr docs from datagovuk prospector"

    def add_arguments(self, parser):
        parser.add_argument("--datasets-file", action="store", help="The dataset JSONL file to ingest")

    def handle(self, *args, **options):
        # Delete existing datasets first
        client = pysolr.Solr(settings.SOLR_URL, always_commit=True)
        client.delete(q="organization:gov.uk")
        client.delete(q="site_id:dgu_organisations* AND name:gov.uk")

        with open(options["datasets_file"]) as f:  # noqa: PTH123
            for raw_json in f.readlines():
                dataset = json.loads(raw_json)
                resources = [
                    {
                        "id": str(uuid.uuid4()),
                        "name": resource["raw_label"],
                        "url": resource["url"],
                        "format": resource["format"].upper(),
                        "size": None,
                        "metadata_modified": datetime.now(UTC).isoformat(),
                        "created": datetime.now(UTC).isoformat(),
                        "resource-type": "resource",
                    }
                    for resource in dataset["resources"]
                ]
                slug = slugify(dataset["title"])
                description = f"{dataset['description']}<br/><br/><a href='{dataset['url']}'>Source</a>"
                create_solr_doc(
                    client,
                    name=slug,
                    title=dataset["title"],
                    notes=description,
                    resources=resources,
                    organization="gov.uk",
                )
