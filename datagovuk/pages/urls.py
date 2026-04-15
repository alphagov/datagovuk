from django.urls import path
from django.views.generic import TemplateView

app_name = "pages"

urlpatterns = [
    path(
        "",
        TemplateView.as_view(
            template_name="pages/home.jinja",
        ),
        name="home",
    ),
    path(
        "about/",
        TemplateView.as_view(
            template_name="pages/about.jinja",
        ),
        name="about",
    ),
    path(
        "cookies/",
        TemplateView.as_view(
            template_name="pages/cookies.jinja",
        ),
        name="cookies",
    ),
    path(
        "components/",
        TemplateView.as_view(
            template_name="pages/components.jinja",
        ),
        name="components",
    ),
]
