import pytest

from datagovuk.pages.sitemap import get_update_items


@pytest.fixture
def updates_root(tmp_path, settings):
    settings.DATAGOVUK_CONTENT_UPDATES_ROOT = f"{tmp_path}/"
    (tmp_path / "2026").mkdir()
    return tmp_path


def write_post(updates_root, name, front_matter):
    (updates_root / "2026" / f"{name}.md").write_text(f"---\n{front_matter}\n---\nContent\n")


def test_get_update_items_returns_title_and_url(updates_root):
    write_post(updates_root, "a-post", "title: A post\ndate: 2026-11-12")

    assert get_update_items() == [{"title": "A post", "url": "/updates/2026/a-post"}]


def test_get_update_items_skips_files_outside_a_year_directory(updates_root):
    (updates_root / "template.md").write_text("---\ntitle: Template\ndate: 2026-11-12\n---\n")

    assert get_update_items() == []


@pytest.mark.parametrize("front_matter", ["date: 2026-11-12", "title: No date", "title: Bad date\ndate: soon"])
def test_get_update_items_skips_posts_without_a_title_or_valid_date(updates_root, front_matter):
    write_post(updates_root, "a-post", front_matter)

    assert get_update_items() == []
