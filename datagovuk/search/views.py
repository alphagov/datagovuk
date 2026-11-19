from django.http import Http404
from django.views.generic import TemplateView

from datagovuk.core.views import GETFormView

from .forms import SearchForm
from .opensearch import get_directory_document_by_slug, search_collections, search_directory


class SearchView(GETFormView):
    template_name = "search/search.jinja"
    form_class = SearchForm
    rows_per_page = 20

    def form_valid(self, form):
        query = form.cleaned_data["query"]

        directory_results, directory_docs = search_directory(query)
        collection_results, collection_docs = search_collections(query)
        context = self.get_context_data(
            query=query,
            directory_results=directory_results,
            directory_docs=directory_docs,
            collection_results=collection_results,
            collection_docs=collection_docs,
        )
        return self.render_to_response(context)

    def get_context_data(
        self,
        query=None,
        directory_results=None,
        directory_docs=None,
        collection_results=None,
        collection_docs=None,
        **kwargs,
    ):
        context = super().get_context_data(**kwargs)
        if query is not None:
            context["search_made"] = True
            context["collection_results"] = collection_results
            context["collection_docs"] = collection_docs
            context["directory_results"] = directory_results
            context["directory_docs"] = directory_docs
        return context


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
