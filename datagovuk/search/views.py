import math
from urllib.parse import urlencode

from django.http import Http404, HttpResponseRedirect
from django.views.generic import TemplateView

from datagovuk.core.views import GETFormView, PaginationMixin

from .forms import SearchForm
from .opensearch import SearchResult, get_directory_document_by_slug, search_collections, search_directory

EMPTY_RESPONSE = {"hits": {"total": {"value": 0}, "hits": []}}

# Each group is (key, heading, facet names). A facet's name is also the query string parameter it sets.
FACET_GROUPS = [
    ("publisher", "Publisher", ["publisher"]),
    ("topic", "Topic", ["topic"]),
    ("format", "Format", ["format"]),
    ("other", "More filters", ["open_government_licence_only", "include_datasets_with_no_links"]),
]

# TODO: not a search aggregation, and the directory search doesn't act on it yet. It has no count until it does.
STATIC_FACETS = {
    "include_datasets_with_no_links": [{"value": "on", "label": "Datasets with no links", "count": None}],
}


def _build_facet_groups(facets, params):
    """
    Turn the directory search facets into groups of links. Selecting a facet links to the current search with its
    parameter set, a selected facet links to the current search with it removed. Changing a filter resets the page.
    """
    base = params.copy()
    base.pop("page", None)
    facet_groups = []
    for key, label, names in FACET_GROUPS:
        group_facets = []
        for name in names:
            for facet in facets.get(name, []):
                is_selected = params.get(name) == facet["value"]
                link_params = base.copy()
                if is_selected:
                    link_params.pop(name)
                else:
                    link_params[name] = facet["value"]
                group_facets.append(
                    {
                        "label": facet["label"],
                        "count": facet["count"],
                        "selected": is_selected,
                        "url": "?" + urlencode(link_params),
                    },
                )
        if group_facets:
            group_facets.sort(key=lambda facet: not facet["selected"])  # stable, so selected facets move to the top
            facet_groups.append({"key": key, "label": label, "facets": group_facets})
    return facet_groups


class SearchView(GETFormView, PaginationMixin):
    template_name = "search/search.jinja"
    form_class = SearchForm
    rows_per_page = 20
    # OpenSearch refuses to return results beyond from + size = index.max_result_window (10,000 by default).
    # This must not exceed that index setting, which needs raising above the number of datasets.
    max_result_window = 100_000

    def form_valid(self, form):
        query = form.cleaned_data.pop("query", "")
        page = self._get_page()
        directory_search = search_directory(
            query,
            filters=form.cleaned_data,
            start=(page - 1) * self.rows_per_page,
            rows=self.rows_per_page,
        )
        total = min(directory_search.total, self.max_result_window)
        last_page = max(1, math.ceil(total / self.rows_per_page))
        if page > last_page:
            params = self.request.GET.copy()
            params["page"] = last_page
            return HttpResponseRedirect(f"{self.request.path}?{params.urlencode()}")

        facet_groups = _build_facet_groups({**directory_search.facets, **STATIC_FACETS}, self.request.GET.dict())
        # Curated collections are only shown on the first page of results
        collection_search = search_collections(query) if page == 1 else SearchResult(response=EMPTY_RESPONSE, docs=[])
        context = self.get_context_data(
            search_made=True,
            search_query=query,
            facet_groups=facet_groups,
            selected_filters=[
                {"key": group["key"], "label": facet["label"], "url": facet["url"]}
                for group in facet_groups
                for facet in group["facets"]
                if facet["selected"]
            ],
            directory_search=directory_search,
            collection_search=collection_search,
            pagination=self.get_govuk_pagination(
                page=page,
                rows_per_page=self.rows_per_page,
                total_results=total,
            ),
        )
        return self.render_to_response(context)

    def _get_page(self):
        try:
            page = int(self.request.GET.get("page", 1))
        except ValueError:
            page = 1
        return max(1, min(page, self.max_result_window // self.rows_per_page))


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
