from http import HTTPStatus

from django.urls import reverse


def test_components(client):
    url = reverse("pages:components")
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert "Components - data.gov.uk" in response.content.decode()


def test_home(client):
    url = reverse("pages:home")
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert "data.gov.uk - The home of UK public data" in response.content.decode()
