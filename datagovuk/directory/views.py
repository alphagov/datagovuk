import json
import math

from django.http import Http404
from django.urls import reverse
from django.views.generic import TemplateView
from ordered_set import OrderedSet

from datagovuk.core.utils import build_table_data
from datagovuk.core.views import GETFormView, PaginationMixin

from .constants import FORMATS_BY_FORMAT_VALUE, TOPICS_BY_SOLR_ALIAS, FormatChoices, TopicChoices
from .forms import SearchForm
from .preview_utils import fetch_csv
from .solr import SolrDatafile, SolrDataset, get_organisations_by_title, get_solr_client, search
from .utils import resource_table_row_data


class SearchView(GETFormView, PaginationMixin):
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

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super().get_form_kwargs(*args, **kwargs)
        publisher_choices = [(title, title) for title in get_organisations_by_title()]
        return {
            "publisher_choices": publisher_choices,
            **form_kwargs,
        }

    def form_valid(self, form):
        query = form.cleaned_data["query"]
        filters = dict(form.cleaned_data)
        del filters["query"]
        context = self.get_context_data(query=query, filters=filters)
        return self.render_to_response(context)

    def get_choices_from_facets(self, facets):
        facets = {
            facet_key: filter(lambda value: isinstance(value, str), facet_value)
            for facet_key, facet_value in facets.items()
        }

        # organisations facet
        all_organisations_by_slug = {slug: title for title, slug in get_organisations_by_title().items()}
        facet_titles = [
            all_organisations_by_slug[slug] for slug in facets["organization"] if slug in all_organisations_by_slug
        ]
        publisher_choices = [(title, title) for title in facet_titles]

        # topics facet
        facet_topics = OrderedSet()
        for facet_value in facets["extras_theme-primary"]:
            if facet_value not in TOPICS_BY_SOLR_ALIAS:
                continue
            facet_topics.add(TOPICS_BY_SOLR_ALIAS[facet_value])
        topic_choices = [(topic, topic) for topic in facet_topics if topic in TopicChoices]

        # format facet
        facet_formats = OrderedSet()
        for facet_value in facets["res_format"]:
            if facet_value not in FORMATS_BY_FORMAT_VALUE:
                facet_formats.add("OTHER")
                continue
            facet_formats.add(FORMATS_BY_FORMAT_VALUE[facet_value])
        format_choices = [
            (format_value, format_value) for format_value in facet_formats if format_value in FormatChoices
        ]

        return {
            "publisher_choices": publisher_choices,
            "topic_choices": topic_choices,
            "format_choices": format_choices,
        }

    def get_context_data(self, query=None, filters=None, **kwargs):
        context = super().get_context_data(**kwargs)
        page = int(self.request.GET.get("page", 1))
        sort = self.request.GET.get("sort", "best")
        rows_per_page = 20
        if query is not None:
            results = search(
                query=query,
                filters=filters,
                start=((page - 1) * rows_per_page),
                rows=rows_per_page,
                sort=sort,
            )
            if results.hits > 0:
                # If we have results, re-initialise the form now that we know what facets should be shown
                form_kwargs = {
                    **self.get_form_kwargs(),
                    **self.get_choices_from_facets(results.facets["facet_fields"]),
                }
                form = self.form_class(**form_kwargs)
                context["form"] = form
            context["results"] = results
            context["page"] = page
            context["rows_per_page"] = rows_per_page
            total_pages = math.ceil(results.hits / rows_per_page)
            context["total_pages"] = total_pages
            context["pages"] = self.get_govuk_pagination(page, total_pages)
            context["sort"] = sort
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
        context["title"] = document["title"]
        context["notes"] = document["notes"]
        context["metadata_modified"] = document["metadata_modified"]

        document_data = json.loads(document["validated_data_dict"])
        context["organization_title"] = document_data["organization"]["title"]
        context["resources"] = [
            resource_table_row_data(resource, document["id"], document["name"])
            for resource in document_data["resources"]
        ]
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
                "back_link": reverse("directory:dataset", kwargs={"uuid": dataset.uuid, "slug": dataset.name}),
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
