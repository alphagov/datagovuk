from django.views.generic import TemplateView

from .solr import get_solr_client


class SearchView(TemplateView):
    template_name = "directory/search.jinja"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q")
        if query:
            client = get_solr_client()
            solr_query = f"(title:({query})^2 OR notes:({query})) AND NOT site_id:dgu_organisations.*"

            results = client.search(solr_query, start=0, rows=10)
            context["results"] = results
        return context
