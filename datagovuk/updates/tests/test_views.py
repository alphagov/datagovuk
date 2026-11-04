from http import HTTPStatus

from django.urls import reverse


def test_update(client):
    url = reverse("updates:post", kwargs={"year": "2026", "slug": "welcome-to-updates"})
    response = client.get(url)
    response_content = response.content.decode()

    assert url == "/updates/2026/welcome-to-updates/"
    assert response.status_code == HTTPStatus.OK
    assert "Cleaning up data.gov.uk - Updates - National Data Library" in response_content
    assert "28 October 2026" in response_content
    assert "By Joe Lanman, Antonia Panayotova" in response_content
    assert 'src="/assets/images/updates/cleaning-illustration-16-9.png"' in response_content
    assert 'width="2400"' in response_content
    assert 'height="1254"' in response_content
    assert 'alt="An illustration of someone cleaning data"' in response_content
    assert '<meta name="description" content="We will use this section' in response_content
    assert '<meta property="og:title" content="Cleaning up data.gov.uk" />' in response_content
    assert '<meta property="og:description" content="We will use this section' in response_content
    assert (
        '<meta property="og:image" content="http://testserver/assets/images/updates/cleaning-illustration-16-9.png" />'
        in response_content
    )


def test_update_not_found(client):
    url = reverse("updates:post", kwargs={"year": "2026", "slug": "missing"})

    assert client.get(url).status_code == HTTPStatus.NOT_FOUND


def test_update_invalid_date_not_found(client, tmp_path, settings):
    post = tmp_path / "2026" / "bad-date.md"
    post.parent.mkdir()
    post.write_text("---\ntitle: Bad\ndate: not-a-date\n---\nBody")
    settings.DATAGOVUK_CONTENT_ROOT = f"{tmp_path}/"
    settings.DATAGOVUK_CONTENT_UPDATES_ROOT = f"{tmp_path}/"
    url = reverse("updates:post", kwargs={"year": "2026", "slug": "bad-date"})

    assert client.get(url).status_code == HTTPStatus.NOT_FOUND


def test_update_without_optional_front_matter(client, tmp_path, settings):
    post = tmp_path / "2026" / "minimal.md"
    post.parent.mkdir()
    post.write_text("---\ntitle: Minimal\ndate: 2026-10-28\n---\nBody")
    settings.DATAGOVUK_CONTENT_ROOT = f"{tmp_path}/"
    settings.DATAGOVUK_CONTENT_UPDATES_ROOT = f"{tmp_path}/"
    url = reverse("updates:post", kwargs={"year": "2026", "slug": "minimal"})
    response = client.get(url)
    response_content = response.content.decode()

    assert response.status_code == HTTPStatus.OK
    assert "Minimal" in response_content
    assert "By " not in response_content
    assert "datagovuk-image" not in response_content
    assert 'property="og:image"' not in response_content
    assert 'name="description"' not in response_content
