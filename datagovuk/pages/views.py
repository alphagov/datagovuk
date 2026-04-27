from django.core.exceptions import PermissionDenied, SuspiciousOperation

from datagovuk.core.views import RenderedMarkdownView


class PagesView(RenderedMarkdownView):
    template_name = "pages/content_page.jinja"

    def get_markdown_file_path(self):
        return f"datagovuk/content/content-pages/{self.kwargs['slug']}.md"


class Error400View(RenderedMarkdownView):
    template_name = "pages/components.jinja"

    def get_context_data(self, *args, **kwargs):
        error_message = "Some bad request"
        raise SuspiciousOperation(error_message)


class Error403View(RenderedMarkdownView):
    template_name = "pages/components.jinja"

    def get_context_data(self, *args, **kwargs):
        error_message = "Forbidden"
        raise PermissionDenied(error_message)


class Error500View(RenderedMarkdownView):
    template_name = "pages/components.jinja"

    def get_context_data(self, *args, **kwargs):
        error_message = "Some exception"
        raise KeyError(error_message)
