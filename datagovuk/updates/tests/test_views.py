import datetime
from http import HTTPStatus
from unittest.mock import patch

from django.urls import reverse


class TestUpdateView:
    def test_renders_post_from_year_and_slug(self, client, make_post):
        url = make_post(slug="my-post", year="2026", front_matter={"title": "My post"})

        response = client.get(url)

        assert url == "/updates/2026/my-post"
        assert response.status_code == HTTPStatus.OK
        assert response.context_data["title"] == "My post"
        assert response.context_data["date"] == datetime.date(2026, 10, 28)
        assert "Body" in response.context_data["content"]

    def test_authors_link_to_team_page(self, client, make_post):
        url = make_post(front_matter={"authors": ["Ada Lovelace"]})

        html = client.get(url).content.decode()

        assert f'href="{reverse("pages:team")}"' in html
        assert "Ada Lovelace" in html

    def test_missing_post_returns_not_found(self, client, make_post):
        make_post(slug="exists")

        response = client.get(reverse("updates:post", kwargs={"year": "2026", "slug": "missing"}))

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_invalid_date_returns_not_found(self, client, make_post):
        url = make_post(front_matter={"date": "not-a-date"})

        assert client.get(url).status_code == HTTPStatus.NOT_FOUND

    def test_missing_date_returns_not_found(self, client, make_post, tmp_path):
        url = make_post()
        (tmp_path / "2026" / "test-post.md").write_text("---\ntitle: No date\n---\nBody")

        assert client.get(url).status_code == HTTPStatus.NOT_FOUND

    def test_page_description_is_summary(self, client, make_post):
        url = make_post(front_matter={"summary": "A short summary"})

        response = client.get(url)

        assert response.context_data["page_description"] == "A short summary"

    def test_page_description_is_none_without_summary(self, client, make_post):
        url = make_post()

        response = client.get(url)

        assert response.context_data["page_description"] is None

    def test_image_dimensions_are_added_to_context(self, client, make_post):
        image = {"src": "images/updates/example.png", "alt": "An example"}
        url = make_post(front_matter={"image": image})

        with patch("datagovuk.updates.views.get_image_size", return_value=(2400, 1254)) as get_image_size:
            response = client.get(url)

        get_image_size.assert_called_once_with("images/updates/example.png")
        assert response.context_data["image"] == {**image, "width": 2400, "height": 1254}

    def test_no_image_in_context_without_image(self, client, make_post):
        url = make_post()

        response = client.get(url)

        assert "image" not in response.context_data

    def test_image_is_used_for_social_sharing(self, client, make_post):
        image = {"src": "images/tests/fixture-image.png", "alt": "An example"}
        url = make_post(front_matter={"image": image})

        response = client.get(url)

        html = response.content.decode()
        expected_url = "http://testserver/assets/images/tests/fixture-image.png"
        assert f'<meta property="og:image" content="{expected_url}"' in html
        assert 'width="40" height="30"' in html

    def test_no_social_sharing_image_without_image(self, client, make_post):
        url = make_post()

        response = client.get(url)

        assert 'property="og:image"' not in response.content.decode()
