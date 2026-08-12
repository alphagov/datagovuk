from django.http import Http404, HttpResponsePermanentRedirect
from django.urls import NoReverseMatch, reverse
from django.views.generic import TemplateView, View
from ordered_set import OrderedSet

from datagovuk.core.utils import build_table_data
from datagovuk.core.views import GETFormView, PaginationMixin

from .constants import FORMATS_BY_FORMAT_VALUE, TOPICS_BY_SOLR_ALIAS, FormatChoices, TopicChoices
from .forms import SearchForm
from .preview_utils import fetch_csv
from .solr import (
    SolrDatafile,
    SolrDataset,
    get_dataset_by_legacy_name,
    get_document,
    get_organisations_by_title,
    get_solr_client,
    search,
)


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
            search_result = search(
                query=query,
                filters=filters,
                start=((page - 1) * rows_per_page),
                rows=rows_per_page,
                sort=sort,
            )
            results = search_result["results"]
            docs = search_result["docs"]
            show_facets = (results.hits > 0) and query
            if show_facets:
                # If we have results AND a query set, re-initialise the form now
                # that we know what facets should be shown
                form_kwargs = {
                    **self.get_form_kwargs(),
                    **self.get_choices_from_facets(results.facets["facet_fields"]),
                }
                form = self.form_class(**form_kwargs)
                context["form"] = form
            context["results"] = results
            context["pagination"] = self.get_govuk_pagination(
                page=page,
                rows_per_page=rows_per_page,
                total_results=results.hits,
            )
            context["docs"] = docs
            context["sort"] = sort
            context["search_made"] = True
        return context


class DatasetView(TemplateView):
    template_name = "directory/dataset.jinja"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dataset_id = self.kwargs["uuid"]
        solr_document = get_document(dataset_id)
        if not solr_document:
            message = f"Active dataset {dataset_id} not found"
            raise Http404(message)
        context["doc"] = solr_document
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


class LegacyDatasetRedirectView(View):
    def get(self, request, legacy_dataset_name, **kwargs):
        return self.legacy_dataset_redirect(request, legacy_dataset_name, **kwargs)

    def legacy_dataset_redirect(self, request, legacy_dataset_name, **kwargs):
        dataset = get_dataset_by_legacy_name(legacy_dataset_name)
        if not dataset:
            raise Http404

        return HttpResponsePermanentRedirect(
            redirect_to=reverse("directory:dataset", kwargs={"uuid": dataset.uuid, "slug": dataset.name}),
        )


class LegacyDatafileRedirectView(View):
    def get(self, request, legacy_dataset_name, datafile_uuid, **kwargs):
        return self.legacy_datafile_redirect(request, legacy_dataset_name, datafile_uuid, **kwargs)

    def legacy_datafile_redirect(self, request, legacy_dataset_name, datafile_uuid, **kwargs):
        dataset = get_dataset_by_legacy_name(legacy_dataset_name)
        if not dataset:
            raise Http404
        if not any(datafile.uuid == datafile_uuid for datafile in dataset.datafiles):
            raise Http404
        try:
            return HttpResponsePermanentRedirect(
                redirect_to=reverse(
                    "directory:preview",
                    kwargs={
                        "dataset_uuid": dataset.uuid,
                        "name": dataset.name,
                        "datafile_uuid": datafile_uuid,
                    },
                ),
            )
        except NoReverseMatch as error:
            raise Http404 from error


class LegacySearchRedirectView(View):
    def get(self, request, **kwargs):
        return self.legacy_search_redirect(request, **kwargs)

    def legacy_search_redirect(self, request, **kwargs):
        return HttpResponsePermanentRedirect(redirect_to=reverse("directory:search"))
