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


def test_about(client):
    url = reverse("pages:about")
    response = client.get(url)
    response_content = response.content.decode()

    assert response.status_code == HTTPStatus.OK
    assert "About - data.gov.uk" in response_content
    assert "About data.gov.uk" in response_content


def test_accessibility(client):
    url = reverse("pages:accessibility")
    response = client.get(url)
    response_content = response.content.decode()

    assert response.status_code == HTTPStatus.OK
    assert "Accessibility - data.gov.uk" in response_content
    assert "Accessibility statement for data.gov.uk" in response_content


def test_support(client):
    url = reverse("pages:support")
    response = client.get(url)
    response_content = response.content.decode()

    assert response.status_code == HTTPStatus.OK
    assert "Support - data.gov.uk" in response_content
    assert "If you’re a civil servant" in response_content  # noqa: RUF001


def test_team(client):
    response = client.get(reverse("pages:team"))
    response_content = response.content.decode()

    assert response.status_code == HTTPStatus.OK
    assert "Team - data.gov.uk" in response_content
    assert "data.gov.uk team" in response_content


def test_privacy_and_terms(client):
    response = client.get(reverse("pages:privacy-and-terms"))
    response_content = response.content.decode()

    assert response.status_code == HTTPStatus.OK
    assert "Privacy and terms - data.gov.uk" in response_content
    assert "Terms of use" in response_content


def test_roadmap(client):
    response = client.get(reverse("pages:roadmap"))
    response_content = response.content.decode()

    assert response.status_code == HTTPStatus.OK
    assert "Our plan for data.gov.uk - data.gov.uk" in response_content
    assert "data.gov.uk roadmap" in response_content
