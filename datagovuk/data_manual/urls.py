from django.urls import path
from django.views.generic import TemplateView

from .views import DataManualView

app_name = "data_manual"

urlpatterns = [
    path(
        "",
        TemplateView.as_view(
            template_name="data_manual/home.jinja",
        ),
        name="home",
    ),
    path(
        "<slug:data_manual_name>/",
        DataManualView.as_view(),
        name="data_manual_page",
    ),
]
