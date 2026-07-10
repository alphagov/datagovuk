from http import HTTPStatus

from django.urls import reverse


def test_components(client):
    url = reverse("pages:components")
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert response.headers["Cache-Control"] == "max-age=1800, public"
    assert "Components - National Data Library" in response.content.decode()


def test_home(client):
    url = reverse("pages:home")
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert response.headers["Cache-Control"] == "max-age=1800, public"
    response_content = response.content.decode()
    assert "National Data Library - The home of UK public data - data.gov.uk" in response_content
    assert "Test feature flag enabled" not in response_content


def test_home_test_feature_flag_enabled(client, settings):
    settings.FEATURE_FLAGS_ENABLED = ["test-feature-flag"]
    url = reverse("pages:home")
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK
    response_content = response.content.decode()
    assert "Test feature flag enabled" in response_content


def test_about(client):
    url = reverse("pages:about")
    response = client.get(url)
    response_content = response.content.decode()

    assert response.status_code == HTTPStatus.OK
    assert "About - National Data Library" in response_content
    assert "About the National Data Library" in response_content


def test_data_curation(client):
    url = reverse("pages:data_curation")
    response = client.get(url)
    response_content = response.content.decode()

    assert response.status_code == HTTPStatus.OK
    assert "How we curate data - National Data Library" in response_content
    assert "In March 2026, we introduced collections to the National Data Library" in response_content


def test_cookies(client):
    url = reverse("pages:cookies")
    response = client.get(url)
    response_content = response.content.decode()

    assert response.status_code == HTTPStatus.OK
    assert "Cookies - National Data Library" in response_content


def test_accessibility(client):
    url = reverse("pages:accessibility")
    response = client.get(url)
    response_content = response.content.decode()

    assert response.status_code == HTTPStatus.OK
    assert "Accessibility - National Data Library" in response_content
    assert "Accessibility statement for the National Data Library" in response_content


def test_support(client):
    url = reverse("pages:support")
    response = client.get(url)
    response_content = response.content.decode()

    assert response.status_code == HTTPStatus.OK
    assert "Support - National Data Library" in response_content
    assert "If you’re a civil servant" in response_content  # noqa: RUF001


def test_team(client):
    response = client.get(reverse("pages:team"))
    response_content = response.content.decode()

    assert response.status_code == HTTPStatus.OK
    assert "Team - National Data Library" in response_content
    assert "National Data Library team" in response_content


def test_privacy_and_terms(client):
    response = client.get(reverse("pages:privacy-and-terms"))
    response_content = response.content.decode()

    assert response.status_code == HTTPStatus.OK
    assert "Privacy and terms - National Data Library" in response_content
    assert "Terms of use" in response_content


def test_roadmap(client):
    response = client.get(reverse("pages:roadmap"))
    response_content = response.content.decode()

    assert response.status_code == HTTPStatus.OK
    assert "Our plan for the National Data Library - National Data Library" in response_content
    assert "National Data Library roadmap" in response_content
