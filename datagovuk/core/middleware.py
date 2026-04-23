from django.conf import settings


class CacheControlMiddleware:
    """Add a default Cache-Control header to responses"""

    def __init__(self, get_response):
        self.get_response = get_response
        self.default_cache_control = getattr(settings, "CACHE_CONTROL_DEFAULT", "max-age=1800, public")

    def __call__(self, request):
        response = self.get_response(request)
        if not response.has_header("Cache-Control"):
            response.headers["Cache-Control"] = self.default_cache_control
        return response
