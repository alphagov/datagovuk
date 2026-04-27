from django.urls import path

from datagovuk.core import views

app_name = "core"

urlpatterns = [
    path(
        "400-test/",
        views.TestError400View.as_view(),
        name="test_error_400",
    ),
    path(
        "403-test/",
        views.TestError403View.as_view(),
        name="test_error_403",
    ),
    path(
        "500-test/",
        views.TestError500View.as_view(),
        name="test_error_500",
    ),
]
