from django.urls import path

from . import views

app_name = "support"

urlpatterns = [
    path(
        "support-form/",
        views.SupportFormView.as_view(),
        name="support-form",
    ),
]
