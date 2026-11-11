from django.http import Http404
from django.views.generic import TemplateView

from datagovuk.core.views import GETFormView

from .forms import SearchForm
from .opensearch import get_directory_document_by_slug, search_collections, search_directory


class SearchView(GETFormView):
    template_name = "search/search.jinja"
    form_class = SearchForm

    def form_valid(self, form):
        query = form.cleaned_data.pop("query", "")
        context = self.get_context_data(
            search_made=True,
            search_query=query,
            debug_show_facets=True,
            directory_search=search_directory(query, filters=form.cleaned_data),
            collection_search=search_collections(query),
        )
        return self.render_to_response(context)


class DatasetView(TemplateView):
    template_name = "search/dataset.jinja"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dataset_slug = self.kwargs["slug"]
        document = get_directory_document_by_slug(dataset_slug)
        if not document:
            message = f"Active dataset {dataset_slug} not found"
            raise Http404(message)
        context["doc"] = document
        return context
