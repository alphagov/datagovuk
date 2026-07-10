import json

from django.http import Http404
from django.views.generic import TemplateView

from .solr import get_solr_client


class SearchView(TemplateView):
    template_name = "directory/search.jinja"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q")
        if query:
            client = get_solr_client()
            solr_query = f"(title:({query})^2 OR notes:({query})) AND NOT organisation:dgu_organisations.*"

            results = client.search(solr_query, start=0, rows=10)
            context["results"] = results
        return context


class DatasetView(TemplateView):
    template_name = "directory/dataset.jinja"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dataset_id = self.kwargs["uuid"]
        client = get_solr_client()
        solr_query = f"id:{dataset_id} AND state:active"
        results = client.search(solr_query, start=0, rows=1)
        if not results:
            message = f"Active dataset {dataset_id} not found"
            raise Http404(message)
        document = results.docs[0]
        context["document"] = document
        context["document_data"] = json.loads(document["validated_data_dict"])
        return context
