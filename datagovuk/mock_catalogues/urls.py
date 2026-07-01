from django.urls import path

from . import views

app_name = "mock_catalogue"

urlpatterns = [
    path("dcat/<slug:filename>", views.MockDCATView.as_view(), name="dcat"),
]
