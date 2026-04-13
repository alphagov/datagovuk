from datetime import date
from http import HTTPStatus

import pytest
from django.urls import reverse


class TestCollectionPageView:
    def test_view_first_collection_item_success(self, client):
        url = reverse(
            "collections:page",
            kwargs={
                "collection_name": "land-and-property",
                "collection_page_name": "uk-house-prices",
            },
        )
        response = client.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["title"] == "UK house prices"
        assert response.context_data["websites"] == [
            {
                "url": "https://landregistry.data.gov.uk/app/ukhpi/",
                "link_text": "Search UK house price index",
            },
        ]
        assert response.context_data["api"] is None
        assert response.context_data["dataset"] == {
            "url": "https://www.gov.uk/government/statistical-data-sets/uk-house-price-index-data-downloads-december-2025",
            "link_text": "Download UK house price index",
        }
        assert response.context_data["page_last_updated"] == date(year=2026, month=3, day=24)
        assert response.context_data["visualisation_data"] == "uk-house-prices/average-house-prices.json"
        assert response.context_data["contact"] is None
        assert response.context_data["status"] == "for-publication"
        assert "the UK house price index" in response.context_data["content"]
        assert response.context_data["slug"] == "uk-house-prices"
        assert response.context_data["collection"] == "Land and property"
        assert response.context_data["collection_slug"] == "land-and-property"
        assert "previous_page" not in response.context_data
        assert response.context_data["next_page"] == {
            "selected": False,
            "slug": "property-price-paid",
            "title": "Property price paid",
            "url": "/collections/land-and-property/property-price-paid",
        }
        assert response.context_data["collection_pages"][0] == {
            "selected": True,
            "slug": "uk-house-prices",
            "title": "UK house prices",
            "url": "/collections/land-and-property/uk-house-prices",
        }

    def test_view_second_collection_item_success(self, client):
        url = reverse(
            "collections:page",
            kwargs={
                "collection_name": "land-and-property",
                "collection_page_name": "property-price-paid",
            },
        )
        response = client.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["title"] == "Property price paid"
        assert response.context_data["next_page"] == {
            "selected": False,
            "slug": "land-and-property-ownership",
            "title": "Land and property ownership",
            "url": "/collections/land-and-property/land-and-property-ownership",
        }
        assert response.context_data["previous_page"] == {
            "selected": False,
            "slug": "uk-house-prices",
            "title": "UK house prices",
            "url": "/collections/land-and-property/uk-house-prices",
        }

    def test_view_last_collection_item_success(self, client):
        url = reverse(
            "collections:page",
            kwargs={
                "collection_name": "land-and-property",
                "collection_page_name": "fire-statistics",
            },
        )
        response = client.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.context_data["title"] == "Fire statistics"
        assert "next_page" not in response.context_data
        assert response.context_data["previous_page"] == {
            "selected": False,
            "slug": "energy-performance-of-buildings",
            "title": "Energy performance of buildings",
            "url": "/collections/land-and-property/energy-performance-of-buildings",
        }

    @pytest.mark.parametrize(
        ("collection_name", "collection_page_name"),
        [
            ("land-and-property", "some-missing-page"),
            ("some-missing-collection", "uk-house-prices"),
        ],
    )
    def test_view_missing_markdown_file_not_found(self, client, collection_name, collection_page_name):
        url = reverse(
            "collections:page",
            kwargs={
                "collection_name": collection_name,
                "collection_page_name": collection_page_name,
            },
        )
        response = client.get(url)

        assert response.status_code == HTTPStatus.NOT_FOUND
