import datetime

from django.conf import settings
from django.http import Http404

from datagovuk.core.utils import get_image_size
from datagovuk.core.views import RenderedMarkdownView


class UpdateView(RenderedMarkdownView):
    template_name = "updates/post.jinja"

    def get_markdown_file_path(self):
        return f"{settings.DATAGOVUK_CONTENT_UPDATES_ROOT}{self.kwargs['year']}/{self.kwargs['slug']}.md"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not isinstance(context.get("date"), datetime.date):
            error_message = "Post is missing a valid date"
            raise Http404(error_message)
        if image := context.get("image"):
            image["width"], image["height"] = get_image_size(image["src"])
        context["page_description"] = context.get("summary")
        return context
