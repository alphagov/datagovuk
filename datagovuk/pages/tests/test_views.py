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
    assert "/updates/2026/cleaning-up-data-gov-uk" in response_content


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
    assert '<meta property="og:title" content="About" />' in response_content


def test_help(client):
    url = reverse("pages:help")
    response = client.get(url)
    response_content = response.content.decode()

    assert response.status_code == HTTPStatus.OK
    assert response.headers["Cache-Control"] == "max-age=1800, public"
    assert "Help" in response_content
    assert "Test feature flag enabled" not in response_content


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


def test_publishers(client):
    url = reverse("pages:publishers")
    response = client.get(url)
    response_content = response.content.decode()

    assert response.status_code == HTTPStatus.OK
    assert "Publishers - National Data Library" in response_content


def test_accessibility(client):
    url = reverse("pages:accessibility")
    response = client.get(url)
    response_content = response.content.decode()

    assert response.status_code == HTTPStatus.OK
    assert "Accessibility - National Data Library" in response_content
    assert "Accessibility statement for the National Data Library" in response_content


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
    assert "The National Data Library roadmap - National Data Library" in response_content
    assert "National Data Library roadmap" in response_content


def test_sitemap(client):
    url = reverse("pages:sitemap")
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert [section["title"] for section in response.context_data["sitemap_sections"]] == [
        "Pages",
        "Collections",
        "Data manual",
        "Updates",
    ]
    assert "Sitemap - National Data Library" in response.content.decode()


def test_sitemap_does_not_render_pages_without_a_title(client, tmp_path, settings):
    year_dir = tmp_path / "2026"
    year_dir.mkdir()
    (year_dir / "titled-post.md").write_text("---\ntitle: Titled post\n---\nContent\n")
    (year_dir / "untitled-post.md").write_text("---\ndate: 2026-11-12\n---\nContent\n")
    settings.DATAGOVUK_CONTENT_UPDATES_ROOT = f"{tmp_path}/"

    response = client.get(reverse("pages:sitemap"))

    response_content = response.content.decode()
    assert 'href="/updates/2026/titled-post"' in response_content
    assert 'href="/updates/2026/untitled-post"' not in response_content
