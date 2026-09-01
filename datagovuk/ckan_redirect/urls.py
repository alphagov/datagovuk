import re

from django.conf import settings
from django.urls import re_path

from .views import CkanRedirectView

app_name = "ckan_redirect"

urlpatterns = [
    re_path(
        rf"^(?!{re.escape(settings.STATIC_URL)})(?P<path>(dataset/edit|user|api|harvest).*)$",
        CkanRedirectView.as_view(),
        name="ckan_redirect",
    ),
]
