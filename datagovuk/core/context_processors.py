from django.conf import settings

from datagovuk.collections.constants import get_collections
from datagovuk.data_manual.constants import DATA_MANUAL_PAGES


def collections(request):
    return {
        "collections": get_collections(),
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


def feature_flags(request):
    return {
        "FEATURE_FLAGS": settings.FEATURE_FLAGS,
    }


def vite_env_processor(request):
    return {
        "VITE_ENV": getattr(settings, "VITE_ENV", "production"),
    }
