import json

from django.http import Http404
from django.views.generic import TemplateView

from .models import SolrDatafile, SolrDataset
from .preview_utils import build_table_data, fetch_csv
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
