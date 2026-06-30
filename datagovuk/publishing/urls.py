from django.urls import path

from datagovuk.publishing import views

app_name = "publishing"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("register/", views.PublisherRegistrationView.as_view(), name="register"),
    path("harvest/add-harvest-source/", views.AddHarvestSourceView.as_view(), name="add_harvest_source"),
]
