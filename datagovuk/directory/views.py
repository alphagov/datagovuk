import math

from django.http import Http404, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.urls import NoReverseMatch, reverse
from django.views.generic import TemplateView, View
from ordered_set import OrderedSet

from datagovuk.core.utils import build_table_data
from datagovuk.core.views import GETFormView, PaginationMixin

from .constants import FORMATS_BY_FORMAT_VALUE, TOPICS_BY_SOLR_ALIAS, FormatChoices, TopicChoices
from .curated import get_collection_counts, get_curated_items, get_suggested_searches
from .forms import SearchForm
from .preview_utils import fetch_csv
from .solr import (
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
    rows_per_page = 20

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

        solr_max_page = 2_147_483_647 // self.rows_per_page

        page = self._get_page(solr_max_page)

        sort = self.request.GET.get("sort", "best")
        search_result = search(
            query=query,
            filters=filters,
            start=(page - 1) * self.rows_per_page,
            rows=self.rows_per_page,
            sort=sort,
        )
        last_page = max(1, math.ceil(search_result["results"].hits / self.rows_per_page))
        if page > last_page:
            params = self.request.GET.copy()
            params["page"] = last_page
            return HttpResponseRedirect(f"{self.request.path}?{params.urlencode()}")

        context = self.get_context_data(query=query, filters=filters, search_result=search_result, page=page, sort=sort)
        return self.render_to_response(context)

    def _get_page(self, solr_max_page):
        try:
            page = int(self.request.GET.get("page", 1))
        except ValueError:
            page = 1
        return max(1, min(page, solr_max_page))

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
            "format_choices": format_choices,
        }

    @staticmethod
    def get_topic_choices(topic_counts, *, include_empty):
        """
        Topics are a fixed list. Offer every one when browsing everything; when searching, only the topics that
        have results. Those with the most results come first.
        """
        topics = [topic for topic in TopicChoices.values if topic and (include_empty or topic_counts.get(topic))]
        topics.sort(key=lambda topic: -topic_counts.get(topic, 0))
        return [(topic, topic) for topic in topics]

    @staticmethod
    def with_selected(choices, filters):
        """Keep ticked options in the list even when they have no matches alongside the other filters."""
        for choices_key, field in (
            ("collection_choices", "collection"),
            ("publisher_choices", "publisher"),
            ("topic_choices", "topic"),
            ("format_choices", "format"),
        ):
            present = {value for value, _ in choices[choices_key]}
            choices[choices_key] += [(value, value) for value in filters.get(field, []) if value not in present]
        return choices

    def get_facet_counts(self, facet_fields):
        """
        Number of matching datasets per topic and per format, for display next to each filter option.

        A dataset can appear under several aliases (topic) or spellings (format) of the same option, so
        the highest count is used rather than the sum, which would count datasets more than once.
        """

        def pairs(facet_values):
            return zip(facet_values[::2], facet_values[1::2], strict=False)

        topic_counts = {topic: 0 for topic in TopicChoices.values if topic}
        for facet_value, count in pairs(facet_fields["extras_theme-primary"]):
            topic = TOPICS_BY_SOLR_ALIAS.get(facet_value)
            if topic:
                topic_counts[topic] = max(topic_counts[topic], count)

        format_counts = {}
        for facet_value, count in pairs(facet_fields["res_format"]):
            file_format = FORMATS_BY_FORMAT_VALUE.get(facet_value, "OTHER")
            format_counts[file_format] = max(format_counts.get(file_format, 0), count)

        publisher_counts = {}
        titles_by_slug = {slug: title for title, slug in get_organisations_by_title().items()}
        for facet_value, count in pairs(facet_fields["organization"]):
            if facet_value in titles_by_slug:
                publisher_counts[titles_by_slug[facet_value]] = count

        return {"publisher": publisher_counts, "topic": topic_counts, "format": format_counts}

    LIST_FILTERS = ("collection", "topic", "format", "publisher")
    BOOLEAN_FILTERS = ("open_government_licence_only", "include_datasets_with_no_links")

    def _url_with(self, **changes):
        """The current search URL with some filters changed: a value of None removes the parameter."""
        params = self.request.GET.copy()
        params.pop("page", None)
        for key, value in changes.items():
            if value is None:
                params.pop(key, None)
            else:
                params.setlist(key, value)
        return f"{self.request.path}?{params.urlencode()}"

    def get_active_filters(self, filters):
        """One chip per ticked filter, each linking to the same search without that filter."""
        chips = []
        for field in self.LIST_FILTERS:
            selected = filters.get(field, [])
            for value in selected:
                remaining = [other for other in selected if other != value]
                chips.append({"label": value, "remove_url": self._url_with(**{field: remaining})})
        for field in self.BOOLEAN_FILTERS:
            if filters.get(field):
                label = self.form_class.base_fields[field].label
                chips.append({"label": label, "remove_url": self._url_with(**{field: None})})
        return chips

    def get_context_data(self, query=None, filters=None, search_result=None, page=None, sort=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if query is not None:
            results = search_result["results"]
            docs = search_result["docs"]
            # Collections come from the curated pages, not Solr: only those with pages for this search are offered
            collection_counts = get_collection_counts(query, filters.get("topic", []))
            collection_choices = [
                (title, title)
                for title, count in sorted(collection_counts.items(), key=lambda item: -item[1])
                if count or not query
            ]
            if results.hits > 0:
                facet_fields = results.facets["facet_fields"]
                facet_counts = self.get_facet_counts(facet_fields)
                choices = {
                    **self.get_choices_from_facets(facet_fields),
                    # Searching with no words (the search icon on its own) browses everything available
                    "topic_choices": self.get_topic_choices(facet_counts["topic"], include_empty=not query),
                }
                context["facet_counts"] = facet_counts
            else:
                # Nothing was found, so there is nothing to filter by, other than what is already ticked
                choices = {"publisher_choices": [], "topic_choices": [], "format_choices": []}
            choices["collection_choices"] = collection_choices
            context["collection_counts"] = collection_counts
            form_kwargs = {**self.get_form_kwargs(), **self.with_selected(choices, filters)}
            context["form"] = self.form_class(**form_kwargs)
            context["results"] = results
            context["pagination"] = self.get_govuk_pagination(
                page=page,
                rows_per_page=self.rows_per_page,
                total_results=results.hits,
            )
            context["docs"] = docs
            context["sort"] = sort
            context["search_made"] = True
            context["suggested_searches"] = get_suggested_searches(query) if results.hits == 0 else []
            context["curated_items"] = get_curated_items(query, filters.get("topic", []), filters.get("collection", []))
            context["active_filters"] = self.get_active_filters(filters)
            context["clear_filters_url"] = self._url_with(**dict.fromkeys(self.LIST_FILTERS + self.BOOLEAN_FILTERS))
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
            raise Http404
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
