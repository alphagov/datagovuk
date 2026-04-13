from django.urls import reverse
from playwright.sync_api import expect

from datagovuk.collections.constants import COLLECTIONS


def test_collection_pages(page, live_server_url):
    for collection_slug, collection_pages in COLLECTIONS.items():
        for collection_page in collection_pages:
            collection_path = reverse(
                "collections:collection_page",
                kwargs={
                    "collection_name": collection_slug,
                    "collection_page_name": collection_page["slug"],
                },
            )
            page.goto(
                live_server_url + collection_path,
            )
            main_content = page.locator(".datagovuk-main")
            expect(main_content.get_by_role("heading", level=1)).to_have_text(
                collection_page["title"],
            )
