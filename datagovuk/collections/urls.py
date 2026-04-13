from django.urls import path

from datagovuk.collections import views

app_name = "collections"

# https://www.data.gov.uk/collections/business-and-economy/uk-trade
urlpatterns = [
    path(
        "<slug:collection_name>/<slug:collection_page_name>",
        views.CollectionPage.as_view(),
        name="page",
    ),
    path(
        "<slug:collection_name>",
        views.Collection.as_view(),
        name="collection",
    ),
]
