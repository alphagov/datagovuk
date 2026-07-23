#!/usr/bin/env python
"""
Loads exported CKAN Solr docs into a dockerised local  Solr matching `ckan`
core doc structure for local dev

Exported data in data/solr_docs.json (pii scrubbed CKAN Solr output) and upserts
docs using pysolr.

Each doc has an `index_id` so reruns of script upsert rather than duplicate

Two doc types end up in the index:

1. dataset docs: Returned by find queries these with `fq=type:dataset`

2. organisation docs: with `site_id` starting `dgu_organisations` matching
`ckan reindex-organisations` writes. No type info needed in query. The data
returned if queries `fq=site_id:dgu_organisation` run

"""

import json
import logging
import os
import sys
from pathlib import Path

import pysolr

logger = logging.getLogger(__name__)

SOLR_URL = os.getenv("SOLR_URL", "http://solr:8983/solr/ckan")
ORG_SITE_ID_PREFIX = "dgu_organisations"
BATCH = 250


def _scalar(value):
    if isinstance(value, list):
        return value[0] if value else ""
    return value


def is_org(doc):
    return str(_scalar(doc.get("site_id")) or "").startswith(ORG_SITE_ID_PREFIX)


def load_data():
    current_path = Path(__file__)
    data_file_path = current_path.parent / "data" / "solr_docs.json"
    with Path.open(data_file_path) as f:
        docs = json.load(f)

    for doc in docs:
        if not is_org(doc):
            doc["type"] = "dataset"  # not stored so not in export and need reset

    solr = pysolr.Solr(SOLR_URL, always_commit=True, timeout=30)

    for start in range(0, len(docs), BATCH):
        solr.add(docs[start : start + BATCH])


if __name__ == "__main__":
    try:
        load_data()
    except Exception:
        logger.exception()
        sys.exit(1)
