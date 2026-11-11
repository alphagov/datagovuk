import math
from urllib.parse import urlencode

from django.http import Http404, HttpResponseRedirect
from django.views.generic import TemplateView

from datagovuk.core.views import GETFormView, PaginationMixin

from .forms import SearchForm
from .opensearch import get_directory_document_by_slug, search_collections, search_directory

# TODO: temporary mock until the backend returns real facet data. Remove MOCK_FACET_GROUPS, _mock_facet_groups and
# _build_facet_groups' use of them, and build facet groups from the OpenSearch aggregations instead.
MOCK_FACET_GROUPS = {
    "publisher": {
        "label": "Publisher",
        "facets": [
            ("ordnance-survey", "Ordnance Survey", 120),
            ("environment-agency", "Environment Agency", 87),
            ("office-for-national-statistics", "Office for National Statistics", 54),
            ("department-for-transport", "Department for Transport", 31),
        ],
    },
    "topic": {
        "label": "Topic",
        "facets": [
            ("environment", "Environment", 140),
            ("transport", "Transport", 62),
            ("health", "Health", 12),
        ],
    },
    "format": {
        "label": "Format",
        "facets": [("CSV", "CSV", 340), ("GeoJSON", "GeoJSON", 45), ("PDF", "PDF", 9)],
    },
}

# Real publisher names for the ?mock_facets=long state. Several are long, which is the point.
MOCK_LONG_PUBLISHERS = [
    ("ordnance-survey", "Ordnance Survey"),
    ("environment-agency", "Environment Agency"),
    ("office-for-national-statistics", "Office for National Statistics"),
    ("department-for-transport", "Department for Transport"),
    ("natural-england", "Natural England"),
    ("met-office", "Met Office"),
    ("hm-land-registry", "HM Land Registry"),
    ("forestry-commission", "Forestry Commission"),
    ("historic-england", "Historic England"),
    ("natural-resources-wales", "Natural Resources Wales"),
    ("scottish-environment-protection-agency", "Scottish Environment Protection Agency"),
    ("department-for-environment-food-and-rural-affairs", "Department for Environment, Food & Rural Affairs"),
    ("department-for-levelling-up-housing-and-communities", "Department for Levelling Up, Housing and Communities"),
    ("ministry-of-housing-communities-and-local-government", "Ministry of Housing, Communities & Local Government"),
    ("department-for-business-and-trade", "Department for Business and Trade"),
    ("department-for-science-innovation-and-technology", "Department for Science, Innovation and Technology"),
    ("department-for-energy-security-and-net-zero", "Department for Energy Security and Net Zero"),
    ("department-for-culture-media-and-sport", "Department for Culture, Media and Sport"),
    ("department-for-work-and-pensions", "Department for Work and Pensions"),
    ("department-of-health-and-social-care", "Department of Health and Social Care"),
    ("nhs-england", "NHS England"),
    ("uk-health-security-agency", "UK Health Security Agency"),
    ("care-quality-commission", "Care Quality Commission"),
    ("driver-and-vehicle-licensing-agency", "Driver and Vehicle Licensing Agency"),
    ("driver-and-vehicle-standards-agency", "Driver and Vehicle Standards Agency"),
    ("maritime-and-coastguard-agency", "Maritime and Coastguard Agency"),
    ("food-standards-agency", "Food Standards Agency"),
    ("health-and-safety-executive", "Health and Safety Executive"),
    ("hm-revenue-and-customs", "HM Revenue & Customs"),
    ("the-national-archives", "The National Archives"),
]


def _mock_facet_groups(variant):
    """
    Return mock facet group data. Use ?mock_facets=empty or ?mock_facets=long to see other states.
    """
    if variant == "empty":
        return {}
    if variant == "long":
        facet_groups = {key: {**group, "facets": list(group["facets"])} for key, group in MOCK_FACET_GROUPS.items()}
        facet_groups["publisher"]["facets"] = [
            (slug, label, 400 - 12 * n) for n, (slug, label) in enumerate(MOCK_LONG_PUBLISHERS)
        ]
        return facet_groups
    return MOCK_FACET_GROUPS


def _build_facet_groups(params):
    """
    Turn facet group data into links. Selecting a facet links to the current search with that facet set,
    a selected facet links to the current search with it removed. Changing a filter resets the page.
    """
    mock_groups = _mock_facet_groups(params.get("mock_facets"))
    base = {key: value for key, value in params.items() if key != "page"}
    facet_groups = []
    for key, group in mock_groups.items():
        selected = params.get(key)
        facets = []
        for value, label, count in group["facets"]:
            is_selected = selected == value
            link_params = {k: v for k, v in base.items() if k != key}
            if not is_selected:
                link_params[key] = value
            facets.append(
                {
                    "label": label,
                    "count": count,
                    "selected": is_selected,
                    "url": f"?{urlencode(link_params)}" if link_params else "?",
                },
            )
        facets.sort(key=lambda facet: not facet["selected"])  # stable, so the selected facet moves to the top
        facet_groups.append({"key": key, "label": group["label"], "facets": facets})
    return facet_groups


class SearchView(GETFormView, PaginationMixin):
    template_name = "search/search.jinja"
    form_class = SearchForm
    rows_per_page = 20
    # OpenSearch refuses to return results beyond from + size = index.max_result_window (10,000 by default).
    # This must not exceed that index setting, which needs raising above the number of datasets.
    max_result_window = 100_000

    def form_valid(self, form):
        query = form.cleaned_data["query"]

        page = self._get_page()
        directory_results, directory_docs = search_directory(
            query,
            start=(page - 1) * self.rows_per_page,
            rows=self.rows_per_page,
        )
        total = directory_results["hits"]["total"]["value"]
        last_page = max(1, math.ceil(min(total, self.max_result_window) / self.rows_per_page))
        if page > last_page:
            params = self.request.GET.copy()
            params["page"] = last_page
            return HttpResponseRedirect(f"{self.request.path}?{params.urlencode()}")

        # Curated collections are only shown on the first page of results
        collection_results, collection_docs = search_collections(query) if page == 1 else (None, [])
        context = self.get_context_data(
            query=query,
            page=page,
            directory_results=directory_results,
            directory_docs=directory_docs,
            collection_results=collection_results,
            collection_docs=collection_docs,
        )
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        # ContextMixin copies every kwarg (query, directory_docs, etc.) into the context
        context = super().get_context_data(**kwargs)
        if kwargs.get("query") is not None:
            context["search_made"] = True
            facet_groups = _build_facet_groups(self.request.GET.dict())
            context["facet_groups"] = facet_groups
            context["selected_filters"] = [
                {"group": group["label"], "label": facet["label"], "url": facet["url"]}
                for group in facet_groups
                for facet in group["facets"]
                if facet["selected"]
            ]
            context["pagination"] = self.get_govuk_pagination(
                page=kwargs["page"],
                rows_per_page=self.rows_per_page,
                total_results=min(kwargs["directory_results"]["hits"]["total"]["value"], self.max_result_window),
            )
        return context

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
