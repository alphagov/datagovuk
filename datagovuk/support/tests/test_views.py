from http import HTTPStatus
from unittest.mock import patch

import pytest

from datagovuk.support.zendesk import ZendeskError


@pytest.fixture(autouse=True)
def support_feature_flag(settings):
    settings.FEATURE_FLAGS_ENABLED = [settings.FEATURE_FLAGS.SUPPORT_FORM.value]


class TestSupportFormView:
    def test_view_renders_successfully(self, client):
        response = client.get("/support-form/")
        assert response.status_code == HTTPStatus.OK
        assert "Contact National Data Library" in response.content.decode()
        assert "Your message was sent" in response.content.decode()

    @patch("datagovuk.support.views.send_ticket_to_zendesk")
    def test_view_valid_submission_redirects_and_sends_zendesk_ticket(self, mock_zendesk, client):
        form_data = {
            "http_referer": "https://example.com/some-page",
            "details": "Test details",
            "name": "Test user",
            "email": "test@example.com",
        }
        response = client.post("/support-form/", data=form_data)
        assert response.status_code == HTTPStatus.FOUND
        mock_zendesk.assert_called_once_with(
            [
                "Page referred from: https://example.com/some-page",
                "\nDetails:\nTest details",
            ],
            "Test user",
            "test@example.com",
        )

    @patch("datagovuk.support.views.send_ticket_to_zendesk")
    def test_view_with_no_http_referer_sends_zendesk_ticket_without_page_referer(self, mock_zendesk, client):
        form_data = {
            "details": "Test details",
            "name": "Test user",
            "email": "test@example.com",
        }
        response = client.post("/support-form/", data=form_data)
        assert response.status_code == HTTPStatus.FOUND
        mock_zendesk.assert_called_once_with(
            [
                "\nDetails:\nTest details",
            ],
            "Test user",
            "test@example.com",
        )

    @patch("datagovuk.support.views.send_ticket_to_zendesk")
    def test_view_invalid_submission_missing_details_does_not_send_ticket_to_zendesk(self, mock_zendesk, client):
        form_data = {
            "http_referer": "https://example.com/some-page",
            "details": "",
            "name": "Test user",
            "email": "test@example.com",
        }
        response = client.post("/support-form/", data=form_data)
        assert response.status_code == HTTPStatus.OK
        assert "This field is required." in response.content.decode()
        mock_zendesk.assert_not_called()

    @patch("datagovuk.support.views.send_ticket_to_zendesk")
    def test_succesful_submission_with_no_email_and_name(self, mock_zendesk, client):
        form_data = {
            "http_referer": "https://example.com/some-page",
            "details": "Test details",
            "name": "",
            "email": "",
        }
        response = client.post("/support-form/", data=form_data)
        assert response.status_code == HTTPStatus.FOUND
        mock_zendesk.assert_called_once_with(
            [
                "Page referred from: https://example.com/some-page",
                "\nDetails:\nTest details",
            ],
            None,
            None,
        )

    @patch("datagovuk.support.views.send_ticket_to_zendesk")
    def test_zendesk_submission_failure_is_handled(self, mock_zendesk, client):
        mock_zendesk.side_effect = ZendeskError(response=None)
        form_data = {
            "details": "Test details",
            "name": "Test user",
            "email": "test@example.com",
        }
        response = client.post("/support-form/", data=form_data)
        assert response.status_code == HTTPStatus.OK
        assert "Your message wasn't sent" in response.content.decode()
