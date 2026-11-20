from datagovuk.pages.sitemaps import get_collection_groups, get_sitemap_sections, get_update_items


def test_get_collection_groups_lists_every_topic_of_each_collection(monkeypatch):
    monkeypatch.setattr(
        "datagovuk.pages.sitemaps.get_collections",
        lambda: [
            {
                "title": "Transport",
                "slug": "transport",
                "topics": [{"title": "Roads", "slug": "roads"}, {"title": "Rail", "slug": "rail"}],
            },
        ],
    )

    assert get_collection_groups() == [
        {
            "title": "Transport",
            "items": [
                {"title": "Roads", "url": "/collections/transport/roads"},
                {"title": "Rail", "url": "/collections/transport/rail"},
            ],
        },
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
