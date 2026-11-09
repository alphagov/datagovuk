from django.urls import path
from django.views.generic import RedirectView

from datagovuk.collections import views

app_name = "collections"

urlpatterns = [
    path("collections.json", views.CollectionsAPIView.as_view(), name="collections_json"),
    path(
        "collections/government/<slug:collection_page_name>",
        RedirectView.as_view(pattern_name="collections:collection_page", permanent=True),
        kwargs={"collection_name": "government-and-parliament"},
    ),
    path(
        "collections/government",
        RedirectView.as_view(
            pattern_name="collections:collection",
            permanent=True,
        ),
        kwargs={"collection_name": "government-and-parliament"},
    ),
    path(
        "collections/<slug:collection_name>/<slug:collection_page_name>/download/",
        views.CollectionDownloadView.as_view(),
        name="collection_download",
    ),
    path(
        "collections/<slug:collection_name>/<slug:collection_page_name>",
        views.CollectionPageView.as_view(),
        name="collection_page",
    ),
    path(
        "collections/<slug:collection_name>",
        views.CollectionView.as_view(),
        name="collection",
    ),
]
