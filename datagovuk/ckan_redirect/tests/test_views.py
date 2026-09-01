from http import HTTPStatus

from django.urls import reverse


class TestCkanRedirectView:
    def test_redirect_to_ckan_for_dataset_edit(self, client):
        url = reverse("ckan_redirect:ckan_redirect", kwargs={"path": "dataset/edit/123"})
        response = client.get(url)

        assert response.status_code == HTTPStatus.MOVED_PERMANENTLY
        assert response["Location"] == "http://ckan.publishing.service.gov.uk/dataset/edit/123"

    def test_redirect_to_ckan_for_user_path(self, client):
        url = reverse("ckan_redirect:ckan_redirect", kwargs={"path": "user/john.doe"})
        response = client.get(url)

        assert response.status_code == HTTPStatus.MOVED_PERMANENTLY
        assert response["Location"] == "http://ckan.publishing.service.gov.uk/user/john.doe"

    def test_redirect_to_ckan_for_api_path(self, client):
        url = reverse("ckan_redirect:ckan_redirect", kwargs={"path": "api/3/action/package_show?id=test"})
        response = client.get(url)

        assert response.status_code == HTTPStatus.MOVED_PERMANENTLY
        assert response["Location"] == "http://ckan.publishing.service.gov.uk/api/3/action/package_show?id=test"

    def test_redirect_to_ckan_for_harvest_path(self, client):
        url = reverse("ckan_redirect:ckan_redirect", kwargs={"path": "harvest/456"})
        response = client.get(url)

        assert response.status_code == HTTPStatus.MOVED_PERMANENTLY
        assert response["Location"] == "http://ckan.publishing.service.gov.uk/harvest/456"

    def test_redirect_preserves_query_string(self, client):
        url = reverse("ckan_redirect:ckan_redirect", kwargs={"path": "user/jane"})
        response = client.get(url, {"page": "2"})

        assert response.status_code == HTTPStatus.MOVED_PERMANENTLY
        assert response["Location"] == "http://ckan.publishing.service.gov.uk/user/jane?page=2"

    def test_404_when_ckan_domain_not_configured(self, client, settings):
        settings.CKAN_DOMAIN = ""
        url = reverse("ckan_redirect:ckan_redirect", kwargs={"path": "user/john.doe"})
        response = client.get(url)

        assert response.status_code == HTTPStatus.NOT_FOUND
