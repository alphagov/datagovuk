from django.conf import settings
from django.urls import include, path
from django.views import defaults as default_views
from django.views.decorators.cache import never_cache
from django_prometheus import exports as prometheus_views
from health_check.views import HealthCheckView

urlpatterns = [
    path("", include("datagovuk.pages.urls", namespace="pages")),
    path("", include("datagovuk.core.urls", namespace="core")),
    path("data-manual/", include("datagovuk.data_manual.urls", namespace="data_manual")),
    path("collections/", include("datagovuk.collections.urls", namespace="collections")),
    path(
        "health/",
        HealthCheckView.as_view(
            checks=[
                "health_check.Cache",
            ],
        ),
    ),
    path(
        "prometheus/metrics",
        never_cache(prometheus_views.ExportToDjangoView),
        name="prometheus-django-metrics",
    ),
]

handler500 = "datagovuk.core.views.server_error"

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
            name="error_bad_request",
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
            name="error_forbidden",
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
            name="error_not_found",
        ),
        path(
            "500/",
            default_views.server_error,
            name="error_server_error",
        ),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
            *urlpatterns,
        ]
