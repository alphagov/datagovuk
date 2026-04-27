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
    path(
        "400-test/",
        views.Error400View.as_view(),
        name="error_400_test",
    ),
    path(
        "403-test/",
        views.Error403View.as_view(),
        name="error_403_test",
    ),
    path(
        "500-test/",
        views.Error500View.as_view(),
        name="error_500_test",
    ),
]
