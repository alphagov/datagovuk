from django.urls import path

from . import views

app_name = "directory"

urlpatterns = [
    path(
        "search",
        views.SearchView.as_view(),
        name="search",
    ),
    path(
        "dataset/<uuid:uuid>/<slug:slug>",
        views.DatasetView.as_view(),
        name="dataset",
    ),
    path(
        "dataset/<uuid:dataset_uuid>/<slug:name>/datafile/<uuid:datafile_uuid>/preview",
        views.PreviewView.as_view(),
        name="preview",
    ),
    path(
        "dataset/<slug:legacy_dataset_name>",
        views.LegacyDatasetRedirectView.as_view(),
        name="legacy_dataset",
    ),
    path(
        "dataset/<slug:legacy_dataset_name>/resource/<uuid:datafile_uuid>",
        views.LegacyDatafileRedirectView.as_view(),
        name="legacy_datafile",
    ),
    path(
        "data/search",
        views.LegacySearchRedirectView.as_view(),
        name="legacy_search",
    ),
]
