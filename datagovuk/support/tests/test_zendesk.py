import logging
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest

from datagovuk.support.zendesk import NDLSupportTicket, ZendeskClient, ZendeskError, send_ticket_to_zendesk

ZENDESK_TICKET_ID = 12345


@pytest.fixture
def zendesk_client(settings):
    settings.ZENDESK_API_KEY = "testkey"
    settings.ZENDESK_TICKET_URL = "https://govuk.zendesk.com/api/v2/tickets.json"
    settings.NOTIFY_ZENDESK_EMAIL = "test@example.com"
    return ZendeskClient()


@pytest.fixture
def ticket():
    return NDLSupportTicket(
        subject="Support request from National Data Library",
        message="Test message",
        requester_name="Test user",
        requester_email="test@example.com",
        tags=["national_data_library"],
    )


@patch("datagovuk.support.zendesk.ZendeskClient")
def test_send_ticket_to_zendesk_creates_and_sends_ticket(mock_zendesk):
    send_ticket_to_zendesk(
        message_body=["Page referred from: https://example.com", "\nDetails:\nTest details"],
        name="Test user",
        email="test@example.com",
    )

    mock_zendesk.return_value.send_ticket_to_zendesk.assert_called_once_with(
        NDLSupportTicket(
            subject="Support request from National Data Library",
            message="Page referred from: https://example.com\n\nDetails:\nTest details",
            requester_name="Test user",
            requester_email="test@example.com",
            tags=["national_data_library"],
        ),
    )


class TestZendeskClient:
    @pytest.mark.parametrize("missing_setting", ["ZENDESK_API_KEY", "ZENDESK_TICKET_URL", "NOTIFY_ZENDESK_EMAIL"])
    def test_zendesk_client_raises_not_implemented_error_when_setting_not_set(self, settings, missing_setting):
        settings.ZENDESK_API_KEY = "testkey"
        settings.ZENDESK_TICKET_URL = "https://govuk.zendesk.com/api/v2/tickets.json"
        settings.NOTIFY_ZENDESK_EMAIL = "test@example.com"
        setattr(settings, missing_setting, None)

        with pytest.raises(NotImplementedError, match=f"{missing_setting} not set"):
            ZendeskClient()

    @patch("datagovuk.support.zendesk.requests.Session.post")
    def test_successful_ticket_creation(self, mock_post, zendesk_client, ticket, caplog):
        mock_post.return_value = MagicMock(
            status_code=HTTPStatus.CREATED,
            json=MagicMock(return_value={"ticket": {"id": ZENDESK_TICKET_ID}}),
        )

        with caplog.at_level(logging.INFO):
            result = zendesk_client.send_ticket_to_zendesk(ticket)

        assert result == ZENDESK_TICKET_ID
        assert f"Zendesk create ticket {ZENDESK_TICKET_ID} succeeded" in caplog.messages

    @patch("datagovuk.support.zendesk.requests.Session.post")
    def test_failed_ticket_creation_raises_zendesk_error(self, mock_post, zendesk_client, ticket):
        mock_response = MagicMock(
            status_code=HTTPStatus.UNAUTHORIZED,
            json=MagicMock(return_value={"foo": "bar"}),
        )
        mock_post.return_value = mock_response

        with pytest.raises(ZendeskError) as exc_info:
            zendesk_client.send_ticket_to_zendesk(ticket)

        assert exc_info.value.response == mock_response

    @patch("datagovuk.support.zendesk.requests.Session.post")
    def test_suspended_user_returns_none(self, mock_post, zendesk_client, ticket, caplog):
        mock_post.return_value = MagicMock(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            json=MagicMock(
                return_value={
                    "error": "RecordInvalid",
                    "details": {"requester": [{"description": "Requester: user is suspended."}]},
                },
            ),
        )

        with caplog.at_level(logging.WARNING):
            result = zendesk_client.send_ticket_to_zendesk(ticket)

        assert result is None
        assert "Zendesk create ticket failed because user is suspended" in caplog.text

    @patch("datagovuk.support.zendesk.requests.Session.post")
    def test_sends_correct_request_data(self, mock_post, zendesk_client, ticket):
        mock_post.return_value = MagicMock(
            status_code=HTTPStatus.CREATED,
            json=MagicMock(return_value={"ticket": {"id": ZENDESK_TICKET_ID}}),
        )

        zendesk_client.send_ticket_to_zendesk(ticket)

        mock_post.assert_called_once_with(
            "https://govuk.zendesk.com/api/v2/tickets.json",
            json=ticket.request_data,
            auth=("test@example.com/token", "testkey"),
            headers={"Content-type": "application/json"},
        )


class TestNDLSupportTicket:
    def test_request_data_without_requester_email_and_name(self):
        ticket = NDLSupportTicket(
            subject="Test subject",
            message="Test message",
            tags=["national_data_library"],
        )

        assert ticket.request_data == {
            "ticket": {
                "subject": "Test subject",
                "comment": {"body": "Test message", "public": False},
                "tags": ["national_data_library"],
            },
        }

    def test_request_data_with_requester_email(self):
        ticket = NDLSupportTicket(
            subject="Test subject",
            message="Test message",
            requester_name="Test user",
            requester_email="test@example.com",
            tags=["national_data_library"],
        )

        assert ticket.request_data["ticket"]["requester"] == {
            "email": "test@example.com",
            "name": "Test user",
        }

    def test_request_data_with_requester_email_but_no_name_falls_back_to_email(self):
        ticket = NDLSupportTicket(
            subject="Test subject",
            message="Test message",
            requester_email="test@example.com",
        )

        assert ticket.request_data["ticket"]["requester"]["name"] == "test@example.com"
