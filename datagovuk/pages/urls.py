from django.urls import path
from django.views.generic import TemplateView

from datagovuk.pages import views

app_name = "pages"

urlpatterns = [
    path(
        "",
        TemplateView.as_view(template_name="pages/home.jinja"),
        name="home",
    ),
    path(
        "about/",
        views.PagesView.as_view(),
        name="about",
        kwargs={"slug": "about"},
    ),
    path(
        "accessibility/",
        views.PagesView.as_view(),
        name="accessibility",
        kwargs={"slug": "accessibility"},
    ),
    path(
        "support/",
        views.PagesView.as_view(),
        name="support",
        kwargs={"slug": "support"},
    ),
    path(
        "team/",
        views.PagesView.as_view(),
        name="team",
        kwargs={"slug": "team"},
    ),
    path(
        "privacy-and-terms/",
        views.PagesView.as_view(),
        name="privacy-and-terms",
        kwargs={"slug": "privacy-and-terms"},
    ),
    path(
        "roadmap/",
        views.PagesView.as_view(template_name="pages/roadmap.jinja"),
        name="roadmap",
        kwargs={"slug": "roadmap"},
    ),
    path(
        "cookies/",
        TemplateView.as_view(template_name="pages/cookies.jinja"),
        name="cookies",
    ),
    path(
        "components/",
        TemplateView.as_view(template_name="pages/components.jinja"),
        name="components",
    ),
]
