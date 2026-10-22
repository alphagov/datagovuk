from django.urls import path
from django.views.generic import TemplateView

app_name = "help"

urlpatterns = [
    path(
        "help/",
        TemplateView.as_view(template_name="help/home.jinja"),
        name="help",
    ),
]
