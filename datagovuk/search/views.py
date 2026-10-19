from datagovuk.core.views import GETFormView

from .forms import SearchForm
from .opensearch import search


class SearchView(GETFormView):
    template_name = "search/search.jinja"
    form_class = SearchForm
    rows_per_page = 20

    def form_valid(self, form):
        query = form.cleaned_data["query"]

        results, docs = search(query)
        context = self.get_context_data(query=query, search_result=results, docs=docs)
        return self.render_to_response(context)

    def get_context_data(self, query=None, search_result=None, docs=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if query is not None:
            results = search_result
            context["results"] = results
            context["docs"] = docs
            context["search_made"] = True
        return context
