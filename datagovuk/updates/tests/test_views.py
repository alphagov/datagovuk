from http import HTTPStatus

from django.urls import reverse


def test_update(client):
    url = reverse("updates:post", kwargs={"date": "2026-10-28", "slug": "welcome-to-updates"})
    response = client.get(url)
    response_content = response.content.decode()

    assert url == "/updates/2026-10-28/welcome-to-updates/"
    assert response.status_code == HTTPStatus.OK
    assert "Welcome to updates - Updates - National Data Library" in response_content
    assert "28 October 2026" in response_content


def test_update_not_found(client):
    url = reverse("updates:post", kwargs={"date": "2026-10-28", "slug": "missing"})

    assert client.get(url).status_code == HTTPStatus.NOT_FOUND


def test_update_invalid_date_not_found(client, tmp_path, settings):
    post = tmp_path / "2026-13-45" / "bad-date.md"
    post.parent.mkdir()
    post.write_text("---\ntitle: Bad\n---\nBody")
    settings.DATAGOVUK_CONTENT_ROOT = f"{tmp_path}/"
    settings.DATAGOVUK_CONTENT_UPDATES_ROOT = f"{tmp_path}/"
    url = reverse("updates:post", kwargs={"date": "2026-13-45", "slug": "bad-date"})

    assert client.get(url).status_code == HTTPStatus.NOT_FOUND
