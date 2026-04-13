from django.urls import path

from datagovuk.collections import views

app_name = "collections"

urlpatterns = [
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
