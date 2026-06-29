from django.urls import path

from datagovuk.publishing import views

app_name = "publishing"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
]
