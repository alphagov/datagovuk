from django.urls import path
from django.views.generic import TemplateView

app_name = "data_manual"

urlpatterns = [
    path(
        "",
        TemplateView.as_view(
            template_name="data_manual/home.jinja",
        ),
        name="home",
    ),
]
