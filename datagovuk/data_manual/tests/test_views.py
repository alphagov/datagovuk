from http import HTTPStatus

from django.urls import reverse


def test_data_manual_home(client):
    url = reverse("data_manual:home")
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert "Data manual" in response.content.decode()
