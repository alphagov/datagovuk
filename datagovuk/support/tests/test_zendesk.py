import base64
import json
import logging
from http import HTTPStatus
from unittest.mock import patch

import pytest
import responses

from datagovuk.support.zendesk import NDLSupportTicket, ZendeskClient, ZendeskError, send_ticket_to_zendesk

ZENDESK_TICKET_ID = 12345


@pytest.fixture
def zendesk_client(settings):
    settings.ZENDESK_API_KEY = "testkey"
    settings.ZENDESK_TICKET_URL = "https://govuk.zendesk.com/api/v2/tickets.json"
    settings.NDL_ZENDESK_EMAIL = "test@example.com"
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
    @pytest.mark.parametrize("missing_setting", ["ZENDESK_API_KEY", "ZENDESK_TICKET_URL", "NDL_ZENDESK_EMAIL"])
    def test_zendesk_client_raises_not_implemented_error_when_setting_not_set(self, settings, missing_setting):
        settings.ZENDESK_API_KEY = "testkey"
        settings.ZENDESK_TICKET_URL = "https://govuk.zendesk.com/api/v2/tickets.json"
        settings.NDL_ZENDESK_EMAIL = "test@example.com"
        setattr(settings, missing_setting, None)

        with pytest.raises(NotImplementedError, match=f"{missing_setting} not set"):
            ZendeskClient()

    @responses.activate
    def test_successful_ticket_creation(self, zendesk_client, ticket, caplog):
        responses.add(
            responses.POST,
            "https://govuk.zendesk.com/api/v2/tickets.json",
            json={"ticket": {"id": ZENDESK_TICKET_ID}},
            status=HTTPStatus.CREATED,
        )

        with caplog.at_level(logging.INFO):
            result = zendesk_client.send_ticket_to_zendesk(ticket)

        assert result == ZENDESK_TICKET_ID
        assert f"Zendesk create ticket {ZENDESK_TICKET_ID} succeeded" in caplog.messages

    @responses.activate
    def test_failed_ticket_creation_raises_zendesk_error(self, zendesk_client, ticket):
        responses.add(
            responses.POST,
            "https://govuk.zendesk.com/api/v2/tickets.json",
            json={"foo": "bar"},
            status=HTTPStatus.UNAUTHORIZED,
        )

        with pytest.raises(ZendeskError):
            zendesk_client.send_ticket_to_zendesk(ticket)

    @responses.activate
    def test_suspended_user_returns_none(self, zendesk_client, ticket, caplog):
        responses.add(
            responses.POST,
            "https://govuk.zendesk.com/api/v2/tickets.json",
            json={
                "error": "RecordInvalid",
                "details": {"requester": [{"description": "Requester: user is suspended."}]},
            },
            status=HTTPStatus.UNPROCESSABLE_ENTITY,
        )

        with caplog.at_level(logging.WARNING):
            result = zendesk_client.send_ticket_to_zendesk(ticket)

        assert result is None
        assert "Zendesk create ticket failed because user is suspended" in caplog.text

    @responses.activate
    def test_sends_correct_request_data(self, zendesk_client, ticket):
        responses.add(
            responses.POST,
            "https://govuk.zendesk.com/api/v2/tickets.json",
            json={"ticket": {"id": ZENDESK_TICKET_ID}},
            status=HTTPStatus.CREATED,
        )

        zendesk_client.send_ticket_to_zendesk(ticket)

        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert request.url == "https://govuk.zendesk.com/api/v2/tickets.json"
        assert json.loads(request.body) == ticket.request_data
        assert request.headers["Content-type"] == "application/json"
        basic_auth = base64.b64encode(b"test@example.com/token:testkey").decode()
        assert request.headers["Authorization"] == f"Basic {basic_auth}"


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
