from urllib.parse import urlencode

from django.http import Http404
from django.views.generic import TemplateView

from datagovuk.core.views import GETFormView

from .forms import SearchForm
from .opensearch import get_directory_document_by_slug, search_collections, search_directory

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
    base = {key: value for key, value in params.items() if key != "page"}
    facet_groups = []
    for key, label, names in FACET_GROUPS:
        group_facets = []
        for name in names:
            for facet in facets.get(name, []):
                is_selected = params.get(name) == facet["value"]
                link_params = {k: v for k, v in base.items() if k != name}
                if not is_selected:
                    link_params[name] = facet["value"]
                group_facets.append(
                    {
                        "label": facet["label"],
                        "count": facet["count"],
                        "selected": is_selected,
                        "url": f"?{urlencode(link_params)}" if link_params else "?",
                    },
                )
        if group_facets:
            group_facets.sort(key=lambda facet: not facet["selected"])  # stable, so selected facets move to the top
            facet_groups.append({"key": key, "label": label, "facets": group_facets})
    return facet_groups


class SearchView(GETFormView):
    template_name = "search/search.jinja"
    form_class = SearchForm

    def form_valid(self, form):
        query = form.cleaned_data.pop("query", "")
        directory_search = search_directory(query, filters=form.cleaned_data)
        facet_groups = _build_facet_groups({**directory_search.facets, **STATIC_FACETS}, self.request.GET.dict())
        context = self.get_context_data(
            search_made=True,
            search_query=query,
            facet_groups=facet_groups,
            selected_filters=[
                {"group": group["label"], "label": facet["label"], "url": facet["url"]}
                for group in facet_groups
                for facet in group["facets"]
                if facet["selected"]
            ],
            directory_search=directory_search,
            collection_search=search_collections(query),
        )
        return self.render_to_response(context)


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
