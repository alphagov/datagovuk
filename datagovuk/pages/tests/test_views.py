from http import HTTPStatus

from django.urls import reverse


def test_components(client):
    url = reverse("pages:components")
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert "Components - data.gov.uk" in response.content.decode()
