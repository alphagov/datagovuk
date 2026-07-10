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
]
