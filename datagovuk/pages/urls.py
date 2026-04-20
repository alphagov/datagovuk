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
        kwargs={"slug": "about", "title": "About"},
    ),
    path(
        "accessibility/",
        views.PagesView.as_view(),
        name="accessibility",
        kwargs={"slug": "accessibility", "title": "Accessibility"},
    ),
    path(
        "support/",
        views.PagesView.as_view(),
        name="support",
        kwargs={"slug": "support", "title": "Support"},
    ),
    path(
        "team/",
        views.PagesView.as_view(),
        name="team",
        kwargs={"slug": "team", "title": "Team"},
    ),
    path(
        "privacy-and-terms/",
        views.PagesView.as_view(),
        name="privacy-and-terms",
        kwargs={"slug": "privacy-and-terms", "title": "Privacy and terms"},
    ),
    path(
        "roadmap/",
        views.PagesView.as_view(template_name="pages/roadmap.jinja"),
        name="roadmap",
        kwargs={"slug": "roadmap", "title": "Our plan for data.gov.uk"},
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
