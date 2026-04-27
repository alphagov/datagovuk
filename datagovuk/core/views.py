from pathlib import Path

from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404, HttpResponseServerError
from django.template import loader
from django.views.decorators.csrf import requires_csrf_token
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


@requires_csrf_token
def server_error(request, template_name="500.html"):
    """
    Custom server_error fallback view which ensures we still have context
    processors passing in header nav items.
    """
    template = loader.get_template(template_name)
    return HttpResponseServerError(template.render(request=request, context={}))


# Views for testing error handling; 404 is missing as django has a catch-all default
class TestError400View(TemplateView):
    template_name = "pages/components.jinja"

    def get_context_data(self, *args, **kwargs):
        error_message = "Some bad request"
        raise SuspiciousOperation(error_message)


class TestError403View(TemplateView):
    template_name = "pages/components.jinja"

    def get_context_data(self, *args, **kwargs):
        error_message = "Forbidden"
        raise PermissionDenied(error_message)


class TestError500View(TemplateView):
    template_name = "pages/components.jinja"

    def get_context_data(self, *args, **kwargs):
        error_message = "Some exception"
        raise KeyError(error_message)
