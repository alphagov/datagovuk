import datetime

import pytest
import yaml
from django.urls import reverse


@pytest.fixture
def make_post(tmp_path, settings):
    """
    Return a factory that writes an update post to a temporary content directory and returns its URL.

    The post has a valid title and date by default; pass `front_matter` to add or override fields.
    """
    settings.DATAGOVUK_CONTENT_ROOT = f"{tmp_path}/"
    settings.DATAGOVUK_CONTENT_UPDATES_ROOT = f"{tmp_path}/"

    def _make_post(slug="test-post", year="2026", front_matter=None, body="Body"):
        front_matter = {"title": "Test post", "date": datetime.date(2026, 10, 28), **(front_matter or {})}
        post = tmp_path / year / f"{slug}.md"
        post.parent.mkdir(exist_ok=True)
        post.write_text(f"---\n{yaml.safe_dump(front_matter)}---\n{body}")
        return reverse("updates:post", kwargs={"year": year, "slug": slug})

    return _make_post
