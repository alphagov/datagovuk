import pytest

from datagovuk.pages.sitemaps import get_collection_groups, get_sitemap_sections, get_update_items


@pytest.fixture
def collections_root(tmp_path, settings, monkeypatch):
    collection_dir = tmp_path / "transport"
    collection_dir.mkdir()
    (collection_dir / "published.md").write_text("---\ntitle: Published\nstatus: for-publication\n---\nContent\n")
    (collection_dir / "draft.md").write_text("---\ntitle: Draft\nstatus: draft\n---\nContent\n")
    (collection_dir / "no-status.md").write_text("---\ntitle: No status\n---\nContent\n")

    settings.DATAGOVUK_CONTENT_COLLECTIONS_ROOT = f"{tmp_path}/"
    monkeypatch.setattr(
        "datagovuk.pages.sitemaps.get_collections",
        lambda: [
            {
                "title": "Transport",
                "slug": "transport",
                "topics": [
                    {"title": "Published", "slug": "published"},
                    {"title": "Draft", "slug": "draft"},
                    {"title": "No status", "slug": "no-status"},
                    {"title": "Missing", "slug": "missing"},
                ],
            },
            {
                "title": "Only drafts",
                "slug": "only-drafts",
                "topics": [{"title": "Missing", "slug": "missing"}],
            },
        ],
    )


@pytest.mark.usefixtures("collections_root")
def test_get_collection_groups_only_includes_published_pages():
    assert get_collection_groups() == [
        {"title": "Transport", "items": [{"title": "Published", "url": "/collections/transport/published"}]},
    ]


def test_get_update_items_skips_template(tmp_path, settings):
    (tmp_path / "template.md").write_text("---\ntitle: Template\n---\n")
    year_dir = tmp_path / "2026"
    year_dir.mkdir()
    (year_dir / "a-post.md").write_text("---\ntitle: A post\n---\nContent\n")
    settings.DATAGOVUK_CONTENT_UPDATES_ROOT = f"{tmp_path}/"

    assert get_update_items() == [{"title": "A post", "url": "/updates/2026/a-post"}]


def test_get_sitemap_sections():
    sections = {section["title"]: section for section in get_sitemap_sections()}

    pages = sections["Pages"]["groups"][0]["items"]
    assert {"title": "About", "url": "/about"} in pages
    assert {"title": "Directory", "url": "/search"} in pages
    assert {"title": "Components", "url": "/components"} not in pages

    collection_groups = {group["title"]: group["items"] for group in sections["Collections"]["groups"]}
    assert {"title": "UK trade", "url": "/collections/business-and-economy/uk-trade"} in collection_groups[
        "Business and economy"
    ]

    assert sections["Data manual"]["url"] == "/data-manual"
    assert {"title": "Data management", "url": "/data-manual/data-management"} in sections["Data manual"]["groups"][0][
        "items"
    ]

    update_urls = [item["url"] for item in sections["Updates"]["groups"][0]["items"]]
    assert "/updates/2026/cleaning-up-data-gov-uk" in update_urls
