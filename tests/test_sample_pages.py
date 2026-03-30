from http import HTTPStatus

from django.urls import reverse


def test_homepage_view(client):
    url = reverse("home")
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert "data.gov.uk: Home" in response.content.decode()


def test_about_view(client):
    url = reverse("about")
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert "About data.gov.uk" in response.content.decode()
