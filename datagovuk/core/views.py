from pathlib import Path

from django.http import Http404
from django.views.generic import TemplateView

from datagovuk.core.markdown import get_template_context_from_markdown


class RenderedMarkdownView(TemplateView):
    def get_markdown_file_path(self):
        error_message = "Subclasses of `RenderedMarkdownView` must implement `get_markdown_file_path()`"
        raise NotImplementedError(error_message)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        markdown_file_path = Path(self.get_markdown_file_path())
        if not markdown_file_path.exists():
            not_found_message = "Content not found"
            raise Http404(not_found_message)
        context.update(
            get_template_context_from_markdown(markdown_file_path),
        )
        return context
