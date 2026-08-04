import re

from django.conf import settings
from django.http import Http404, HttpResponsePermanentRedirect
from django.views import View

PATH_REGEX = rf"^(?!{re.escape(settings.STATIC_URL)})(?P<path>(dataset/edit|user|api|harvest).*)$"


class CkanRedirectView(View):
    def dispatch(self, request, *args, **kwargs):
        if not settings.CKAN_DOMAIN:
            raise Http404

        path = kwargs.get("path", "")
        scheme = "https" if request.is_secure() else "http"
        target_url = f"{scheme}://{settings.CKAN_DOMAIN}/{path}"

        query_string = request.GET.urlencode()
        if query_string:
            target_url = f"{target_url}?{query_string}"

        return HttpResponsePermanentRedirect(target_url)
