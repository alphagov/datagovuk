import datetime
from pathlib import Path

import frontmatter
from django.conf import settings
from django.urls import reverse, reverse_lazy

# Pages with a fixed URL. Collections, data manual pages and updates are listed separately.
STATIC_PAGES = [
    {"title": title, "url": reverse_lazy(url_name)}
    for url_name, title in [
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
        ("directory:search", "Directory"),
    ]
]


def get_update_items():
    """Links to the updates that can be viewed, i.e. those with a title and a valid date."""
    items = []
    for markdown_path in sorted(Path(settings.DATAGOVUK_CONTENT_UPDATES_ROOT).glob("*/*.md")):
        post = frontmatter.load(markdown_path)
        if post.get("title") and isinstance(post.get("date"), datetime.date):
            url = reverse("updates:post", kwargs={"year": markdown_path.parent.name, "slug": markdown_path.stem})
            items.append({"title": post["title"], "url": url})
    return items
