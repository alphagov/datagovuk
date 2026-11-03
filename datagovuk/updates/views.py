import datetime

from django.conf import settings
from django.http import Http404

from datagovuk.core.views import RenderedMarkdownView


class UpdateView(RenderedMarkdownView):
    template_name = "updates/post.jinja"

    def get_markdown_file_path(self):
        return f"{settings.DATAGOVUK_CONTENT_UPDATES_ROOT}{self.kwargs['date']}/{self.kwargs['slug']}.md"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["date"] = datetime.date.fromisoformat(self.kwargs["date"])
        except ValueError as error:
            error_message = "Invalid date"
            raise Http404(error_message) from error
        context["page_description"] = context.get("summary")
        return context
