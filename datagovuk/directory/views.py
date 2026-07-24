import json

from django.http import Http404
from django.views.generic import TemplateView

from datagovuk.core.views import GETFormView

from .forms import SearchForm
from .preview_utils import build_table_data, fetch_csv
from .solr import SolrDatafile, SolrDataset, get_solr_client, search


class SearchView(GETFormView):
    template_name = "directory/search.jinja"
    form_class = SearchForm

    def _translate_legacy_params(self, request):
        legacy_params = {
            "q": "query",
            "filters[publisher]": "publisher",
            "filters[topic]": "topic",
            "filters[format]": "format",
            "filters[licence_code]": "open_government_licence_only",
        }
        get_params = request.GET.copy()
        for legacy_param, new_param in legacy_params.items():
            is_new_param_set = get_params.get(new_param)
            if is_new_param_set:
                continue
            is_legacy_param_set = get_params.get(legacy_param)
            if is_legacy_param_set:
                get_params[new_param] = get_params[legacy_param]
        request.GET = get_params

    def get(self, request, *args, **kwargs):
        self._translate_legacy_params(request)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        query = form.cleaned_data["query"]
        filters = dict(form.cleaned_data)
        del filters["query"]
        context = self.get_context_data(query=query, filters=filters)
        return self.render_to_response(context)

    def get_context_data(self, query=None, filters=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if query is not None:
            results = search(
                query=query,
                filters=filters,
                start=0,
                rows=20,
            )
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
        if not results.hits > 0:
            message = f"Active dataset {dataset_id} not found"
            raise Http404(message)
        document = results.docs[0]
        context["document"] = document
        context["document_data"] = json.loads(document["validated_data_dict"])
        return context


class PreviewView(TemplateView):
    template_name = "directory/preview.jinja"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        dataset = self.get_dataset()
        datafile = self.get_datafile(dataset)

        if not datafile.is_csv:
            raise Http404

        all_rows = fetch_csv(datafile.url)
        headers = all_rows[0] if all_rows else []
        limited_data = all_rows[1:5] if len(all_rows) > 1 else []

        table_headings, table_rows = build_table_data(headers, limited_data)

        context.update(
            {
                "datafile": datafile,
                "dataset": dataset,
                "table_headings": table_headings,
                "table_rows": table_rows,
                "preview_rows": len(limited_data),
                "preview_exists": bool(limited_data),
            },
        )
        return context

    def get_dataset(self):
        solr_documents = (
            get_solr_client().search(f"id:{self.kwargs['dataset_uuid']} AND state:active", start=0, rows=1).docs
        )
        if not solr_documents:
            raise Http404
        return SolrDataset.from_solr_doc(solr_documents[0])

    def get_datafile(self, dataset):
        resource_uuid = str(self.kwargs["datafile_uuid"])
        datafile = next((f for f in dataset.datafiles if f.uuid == resource_uuid), None)
        if datafile is None:
            raise SolrDatafile.DatafileNotFoundError
        return datafile
