from http import HTTPStatus

import pytest
from django.urls import reverse

from datagovuk.data_manual.constants import DATA_MANUAL_PAGES


def test_data_manual_home(client):
    url = reverse("data_manual:home")
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert "Data manual" in response.content.decode()


class TestDataManualView:
    @pytest.mark.parametrize("data_manual_item", [(item["slug"], item["title"]) for item in DATA_MANUAL_PAGES])
    def test_data_manual_view(self, client, data_manual_item):
        data_manual_slug, data_manual_title = data_manual_item

        url = reverse("data_manual:data_manual_page", kwargs={"data_manual_name": data_manual_slug})
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK
        assert response.context_data["title"] == data_manual_title

    def test_invalid_data_manual_name(self, client):
        url = reverse("data_manual:data_manual_page", kwargs={"data_manual_name": "invalid-slug"})

        response = client.get(url)

        assert response.status_code == HTTPStatus.NOT_FOUND
