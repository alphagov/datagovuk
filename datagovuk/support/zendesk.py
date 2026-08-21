import dataclasses
import logging
from http import HTTPStatus

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_ticket_to_zendesk(message_body, name, email):
    ticket = NDLSupportTicket(
        subject="Support request from National Data Library",
        message="\n".join(message_body),
        requester_name=name,
        requester_email=email,
        tags=["national_data_library"],
    )
    client = ZendeskClient()
    client.send_ticket_to_zendesk(ticket)


class ZendeskClient:
    """
    A ZendeskClient copied from the alphagov/notifications-utils repo
    """

    def __init__(self):
        for setting in ("ZENDESK_API_KEY", "ZENDESK_TICKET_URL", "NOTIFY_ZENDESK_EMAIL"):
            if not getattr(settings, setting):
                error_message = f"{setting} not set"
                raise NotImplementedError(error_message)
        self.api_key = settings.ZENDESK_API_KEY
        self.ticket_url = settings.ZENDESK_TICKET_URL
        self.notify_zendesk_email = settings.NOTIFY_ZENDESK_EMAIL
        self.requests_session = requests.Session()

    def send_ticket_to_zendesk(self, ticket):
        response = self.requests_session.post(
            self.ticket_url,
            json=ticket.request_data,
            auth=(f"{self.notify_zendesk_email}/token", self.api_key),
            headers={"Content-type": "application/json"},
        )

        if response.status_code != HTTPStatus.CREATED:
            if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY and self._is_user_suspended(response.json()):
                error_message = response.json()["details"]
                logger.warning("Zendesk create ticket failed because user is suspended: %r", error_message)
                return None
            logger.error(
                "Zendesk create ticket request failed with %s: %r",
                response.status_code,
                response.json(),
                extra={"status_code": response.status_code},
            )
            raise ZendeskError(response)

        ticket_id = response.json()["ticket"]["id"]

        logger.info(
            "Zendesk create ticket %s succeeded",
            ticket_id,
            extra={"zendesk_ticket_id": ticket_id, "zendesk_operation": "create"},
        )

        return ticket_id

    def _is_user_suspended(self, response):
        requester_error = response["details"].get("requester")
        return requester_error and ("suspended" in requester_error[0]["description"])


class ZendeskError(Exception):
    def __init__(self, response):
        self.response = response


@dataclasses.dataclass
class NDLSupportTicket:
    subject: str
    message: str
    requester_name: str | None = None
    requester_email: str | None = None
    tags: list[str] = dataclasses.field(default_factory=list)

    @property
    def request_data(self):
        data = {
            "ticket": {
                "subject": self.subject,
                "comment": {"body": self.message, "public": False},
                "tags": self.tags,
            },
        }

        if self.requester_email:
            data["ticket"]["requester"] = {
                "email": self.requester_email,
                "name": self.requester_name or self.requester_email,
            }

        return data
