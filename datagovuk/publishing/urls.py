from django.urls import path

from datagovuk.publishing import views

app_name = "publishing"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("register/", views.PublisherRegistrationView.as_view(), name="register"),
    path("catalogue/add/", views.AddCatalogueView.as_view(), name="add_catalogue"),
    path("catalogue/<slug:slug>/", views.CatalogueDetailView.as_view(), name="catalogue_detail"),
    path("harvest-run/<uuid:harvest_run_id>/events/", views.HarvestRunEventsView.as_view(), name="harvest_run_events"),
]
