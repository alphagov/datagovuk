from django.conf import settings

from datagovuk.collections.constants import COLLECTIONS
from datagovuk.data_manual.constants import DATA_MANUAL_PAGES


def _retrieve_collections(collections: list):
    returned_list = []

    for collection in collections:
        if collection["type"] != "collection":
            continue

        returned_list.append(
            {
                "title": collection["title"],
                "slug": collection["slug"],
                "description": collection["description"],
            },
        )

    return returned_list


def _retrieve_spotlights(collections: list):
    returned_list = []

    for collection in collections:
        if collection["type"] != "spotlight":
            continue

        returned_list.append(
            {
                "title": collection["title"],
                "slug": collection["slug"],
                "description": collection["description"],
            },
        )

    return returned_list


def collections(request):
    return {
        "collections": _retrieve_collections(COLLECTIONS),
        "spotlights": _retrieve_spotlights(COLLECTIONS),
    }


def data_manual(request):
    return {"data_manual_items": DATA_MANUAL_PAGES}


def data_manual_menu_items(request):
    return {
        "data_manual_menu_items": [
            *DATA_MANUAL_PAGES,
            {
                "title": "Tell us what you think",
                "url": "https://forms.office.com/e/9V26PNFQaR",
                "description": (
                    "We'd love your feedback. Is this manual useful? Can we improve it? Complete a feedback form."
                ),
            },
            {
                "title": "Join a data community",
                "url": "/data-manual/join-a-data-community",
                "description": (
                    "Find Slack channels, events and other ways to connect with data practitioners. Learn more."
                ),
            },
        ],
    }


def google_tag_manager(request):
    return {
        "GOOGLE_TAG_MANAGER_ID": settings.GOOGLE_TAG_MANAGER_ID,
        "GOOGLE_TAG_MANAGER_AUTH": settings.GOOGLE_TAG_MANAGER_AUTH,
        "GOOGLE_TAG_MANAGER_PREVIEW": settings.GOOGLE_TAG_MANAGER_PREVIEW,
    }
