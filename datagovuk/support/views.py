import logging

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from sentry_sdk import capture_exception

from .forms import SupportForm
from .zendesk import ZendeskError, send_ticket_to_zendesk

logger = logging.getLogger(__name__)


class SupportFormView(FormView):
    template_name = "support/support_form.jinja"
    form_class = SupportForm
    success_url = reverse_lazy("support:support-form")

    def get_initial(self):
        initial = super().get_initial()
        initial["http_referer"] = self.request.headers.get("referer", "")
        return initial

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        http_referer = cleaned_data.get("http_referer", "")
        details = cleaned_data["details"]
        requester_name = cleaned_data["name"] or None
        requester_email = cleaned_data["email"] or None

        message_body = []
        if http_referer:
            # TODO: how should we show the parsed_url in the message_body? must include query params?
            message_body.append(f"Page referred from: {http_referer}")
        message_body.append(f"\nDetails:\n{details}")

        try:
            send_ticket_to_zendesk(message_body, requester_name, requester_email)
        except ZendeskError as e:
            capture_exception(e)
            messages.error(self.request, "Your message wasn't sent")
            return self.form_invalid(form)

        messages.success(self.request, "Your message was sent")
        return super().form_valid(form)
