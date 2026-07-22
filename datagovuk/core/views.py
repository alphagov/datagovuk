from django.conf import settings
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import HttpResponse, HttpResponseServerError
from django.template import loader
from django.views.decorators.csrf import requires_csrf_token
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView

from datagovuk.core.markdown import get_safe_markdown_path, get_template_context_from_markdown


class RenderedMarkdownView(TemplateView):
    def get_markdown_file_path(self):
        error_message = "Subclasses of `RenderedMarkdownView` must implement `get_markdown_file_path()`"
        raise NotImplementedError(error_message)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        markdown_file_path = get_safe_markdown_path(self.get_markdown_file_path())
        context.update(
            get_template_context_from_markdown(markdown_file_path),
        )
        return context


class GETFormView(FormView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.GET:
            kwargs["data"] = self.request.GET
        return kwargs

    def get(self, request, *args, **kwargs):
        if request.GET:
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
            return self.form_invalid(form)
        return super().get(request, *args, **kwargs)


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


class VersionView(View):
    def get(self, *args, **kwargs):
        return HttpResponse(settings.DATAGOVUK_GIT_SHA)
