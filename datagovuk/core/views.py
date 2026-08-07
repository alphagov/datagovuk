import math

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


class PaginationMixin:
    """
    Helper mixin to generate GOV.UK Design System pagination dictionaries.
    """

    SHOW_ALL_PAGES_THRESHOLD = 7
    FIRST_PAGES_THRESHOLD = 4
    LAST_PAGES_THRESHOLD = 4
    _ellipsis = "ellipsis"

    def build_page_url(self, page_num: int) -> str:
        query_params = self.request.GET.copy()
        query_params["page"] = page_num
        return f"{self.request.path}?{query_params.urlencode()}"

    def get_page_sequence(self, page: int, total_pages: int) -> list:
        show_all_pages = total_pages < self.SHOW_ALL_PAGES_THRESHOLD
        if show_all_pages:
            return list(range(1, total_pages + 1))

        page_within_first_pages = page < self.FIRST_PAGES_THRESHOLD
        if page_within_first_pages:
            return [*range(1, (self.FIRST_PAGES_THRESHOLD + 1)), self._ellipsis, total_pages]

        page_within_last_pages = page > (total_pages - self.LAST_PAGES_THRESHOLD)
        if page_within_last_pages:
            return [1, self._ellipsis, *range(total_pages - (self.LAST_PAGES_THRESHOLD - 1), total_pages + 1)]

        # Otherwise the page is somewhere in the middle..
        return [1, self._ellipsis, page - 1, page, page + 1, self._ellipsis, total_pages]

    def get_govuk_pagination(
        self,
        page: int,
        rows_per_page: int,
        total_results: int,
    ) -> dict:
        """
        Builds a dict compatible with `govukPagination` macro.
        """
        total_pages = math.ceil(total_results / rows_per_page)
        last_result_in_page = page * rows_per_page if page < total_pages else total_results
        pagination = {
            "page": page,
            "first_result_in_page": ((page - 1) * rows_per_page) + 1 if total_results else None,
            "last_result_in_page": last_result_in_page if total_results else None,
            "total_results": total_results,
        }
        if total_pages <= 1:
            return pagination

        items = []
        for item in self.get_page_sequence(page, total_pages):
            if item is self._ellipsis:
                items.append({"ellipsis": True})
            else:
                data = {
                    "number": item,
                    "href": self.build_page_url(item),
                }
                if item == page:
                    data["current"] = True
                items.append(data)

        pages = {"items": items}

        # Navigation controls
        show_previous = page > 1
        if show_previous:
            pages["previous"] = {
                "href": self.build_page_url(page - 1),
            }
        show_next = page < total_pages
        if show_next:
            pages["next"] = {"href": self.build_page_url(page + 1)}
        pagination["pages"] = pages

        return pagination


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
