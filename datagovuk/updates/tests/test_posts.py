import datetime
from pathlib import Path

import frontmatter
from django.conf import settings

from datagovuk.updates.posts import get_update_posts


def test_get_update_posts_returns_title_and_url(make_post):
    url = make_post(slug="a-post", front_matter={"title": "A post"})

    assert get_update_posts() == [{"title": "A post", "url": url}]


def test_get_update_posts_skips_files_outside_a_year_directory(make_post, tmp_path):
    url = make_post(slug="a-post")
    (tmp_path / "template.md").write_text("---\ntitle: Template\n---\n")

    assert get_update_posts() == [{"title": "Test post", "url": url}]


def test_every_real_update_post_has_a_title_and_a_valid_date():
    # Checks the real content, not test data: get_update_posts() needs a title, and UpdateView needs a valid date.
    markdown_paths = sorted(Path(settings.DATAGOVUK_CONTENT_UPDATES_ROOT).glob("*/*.md"))

    assert markdown_paths
    for markdown_path in markdown_paths:
        post = frontmatter.load(markdown_path)
        assert post.get("title"), f"{markdown_path} is missing a title"
        assert isinstance(post.get("date"), datetime.date), f"{markdown_path} is missing a valid date"
