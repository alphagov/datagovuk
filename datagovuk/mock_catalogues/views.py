import os

from django.http import Http404, HttpResponse
from django.views import View


class MockDCATView(View):
    def get(self, request, *args, **kwargs):
        file_path = os.path.join(os.path.dirname(__file__), f"dcat/{kwargs['filename']}")
        if not os.path.exists(file_path):
            raise Http404("The requested file does not exist.")
        file_handle = open(file_path, "rb")
        response = HttpResponse(file_handle.read())
        del response.headers["Content-Type"]
        return response
