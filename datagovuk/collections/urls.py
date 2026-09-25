from django.urls import path
from django.views.generic import RedirectView

from datagovuk.collections import views

app_name = "collections"

urlpatterns = [
    path(
        "government/<slug:collection_page_name>",
        RedirectView.as_view(pattern_name="collections:collection_page", permanent=True),
        kwargs={"collection_name": "government-and-parliament"},
    ),
    path(
        "government",
        RedirectView.as_view(
            pattern_name="collections:collection",
            permanent=True,
        ),
        kwargs={"collection_name": "government-and-parliament"},
    ),
    path(
        "<slug:collection_name>/<slug:collection_page_name>/download/",
        views.CollectionDownloadView.as_view(),
        name="collection_download",
    ),
    path(
        "<slug:collection_name>/<slug:collection_page_name>",
        views.CollectionPageView.as_view(),
        name="collection_page",
    ),
    path(
        "<slug:collection_name>",
        views.CollectionView.as_view(),
        name="collection",
    ),
]
