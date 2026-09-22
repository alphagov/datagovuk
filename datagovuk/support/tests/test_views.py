from http import HTTPStatus
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.urls import reverse

from datagovuk.support.zendesk import ZendeskError


class TestSupportFormView:
    def test_view_renders_successfully(self, client):
        url = reverse("support:support-form")
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK
        assert "Contact National Data Library" in response.content.decode()

    @patch("datagovuk.support.views.send_ticket_to_zendesk")
    def test_view_valid_submission_redirects_and_sends_zendesk_ticket(self, mock_zendesk, client):
        form_data = {
            "http_referer": "https://example.com/some-page",
            "details": "Test details",
            "name": "Test user",
            "email": "test@example.com",
        }
        url = reverse("support:support-form")
        response = client.post(url, data=form_data, HTTP_USER_AGENT="test-agent")
        assert response.status_code == HTTPStatus.FOUND
        mock_zendesk.assert_called_once_with(
            [
                "[Requester]\nTest user \n<test@example.com>",
                "[Details]\nTest details",
                "[Referrer]\nhttps://example.com/some-page",
                "[User agent]\ntest-agent",
            ],
            "Test user",
            "test@example.com",
        )
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert str(messages[0]) == "Your message was sent."

    @patch("datagovuk.support.views.send_ticket_to_zendesk")
    def test_view_with_no_http_referer_and_user_agent_sends_zendesk_ticket_without_page_referer_and_user_agent(
        self,
        mock_zendesk,
        client,
    ):
        form_data = {
            "details": "Test details",
            "name": "Test user",
            "email": "test@example.com",
        }
        url = reverse("support:support-form")
        response = client.post(url, data=form_data)
        assert response.status_code == HTTPStatus.FOUND
        mock_zendesk.assert_called_once_with(
            [
                "[Requester]\nTest user \n<test@example.com>",
                "[Details]\nTest details",
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
        url = reverse("support:support-form")
        response = client.post(url, data=form_data)
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
        url = reverse("support:support-form")
        response = client.post(url, data=form_data)
        assert response.status_code == HTTPStatus.FOUND
        mock_zendesk.assert_called_once_with(
            [
                "[Details]\nTest details",
                "[Referrer]\nhttps://example.com/some-page",
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
        url = reverse("support:support-form")
        response = client.post(url, data=form_data)
        assert response.status_code == HTTPStatus.OK
        stored_messages = list(get_messages(response.wsgi_request))
        assert len(stored_messages) == 1
        assert str(stored_messages[0]) == "Your message was not sent due to a service problem. Try again later."
