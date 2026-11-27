from pathlib import Path

import frontmatter
from django.conf import settings
from django.urls import reverse


def get_update_posts():
    return [
        {
            "title": frontmatter.load(markdown_path)["title"],
            "url": reverse("updates:post", kwargs={"year": markdown_path.parent.name, "slug": markdown_path.stem}),
        }
        for markdown_path in sorted(Path(settings.DATAGOVUK_CONTENT_UPDATES_ROOT).glob("*/*.md"))
    ]
