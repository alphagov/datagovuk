from pathlib import Path

import frontmatter
from django.conf import settings
from django.urls import reverse

from datagovuk.collections.constants import get_collections
from datagovuk.data_manual.constants import DATA_MANUAL_PAGES

# Pages with a fixed URL.
STATIC_PAGES = [
    ("pages:home", "Home"),
    ("pages:about", "About"),
    ("pages:roadmap", "Roadmap"),
    ("pages:data_curation", "How we curate data"),
    ("pages:team", "Team"),
    ("pages:publishers", "Publish your data"),
    ("pages:help", "Help"),
    ("pages:accessibility", "Accessibility"),
    ("pages:cookies", "Cookies"),
    ("pages:privacy-and-terms", "Privacy and terms"),
    ("support:support-form", "Support"),
    ("data_manual:home", "Data manual"),
    ("directory:search", "Directory"),
]


def get_collection_groups():
    """One group per collection, listing its pages."""
    return [
        {
            "title": collection["title"],
            "items": [
                {
                    "title": topic["title"],
                    "url": reverse(
                        "collections:collection_page",
                        kwargs={"collection_name": collection["slug"], "collection_page_name": topic["slug"]},
                    ),
                }
                for topic in collection["topics"]
            ],
        }
        for collection in get_collections()
    ]


def get_update_items():
    return [
        {
            "title": frontmatter.load(markdown_path).get("title"),
            "url": reverse("updates:post", kwargs={"year": markdown_path.parent.name, "slug": markdown_path.stem}),
        }
        for markdown_path in sorted(Path(settings.DATAGOVUK_CONTENT_UPDATES_ROOT).glob("*/*.md"))
    ]


def get_sitemap_sections():
    """
    The sections shown on the sitemap page.

    Each section has a title, an optional URL for its heading, and groups of links. A group's title is shown as a
    subheading, or left out when it is None.
    """
    return [
        {
            "title": "Pages",
            "url": None,
            "groups": [
                {
                    "title": None,
                    "items": [{"title": title, "url": reverse(url_name)} for url_name, title in STATIC_PAGES],
                },
            ],
        },
        {
            "title": "Collections",
            "url": None,
            "groups": get_collection_groups(),
        },
        {
            "title": "Data manual",
            "url": reverse("data_manual:home"),
            "groups": [
                {
                    "title": None,
                    "items": [
                        {
                            "title": page["title"],
                            "url": reverse("data_manual:data_manual_page", kwargs={"data_manual_name": page["slug"]}),
                        }
                        for page in DATA_MANUAL_PAGES
                    ],
                },
            ],
        },
        {
            "title": "Updates",
            "url": None,
            "groups": [{"title": None, "items": get_update_items()}],
        },
    ]
