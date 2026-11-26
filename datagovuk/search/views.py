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


class SearchView(GETFormView):
    template_name = "search/search.jinja"
    form_class = SearchForm

    def form_valid(self, form):
        query = form.cleaned_data.pop("query", "")
        directory_search = search_directory(query, filters=form.cleaned_data)
        facet_groups = _build_facet_groups(directory_search.facets, self.request.GET.dict())
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
            collection_search=search_collections(query, filters=form.cleaned_data),
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
