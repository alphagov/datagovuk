from django.http import HttpResponse

from datagovuk.core.middleware import CacheControlMiddleware


def test_cache_control_added_when_missing(rf):
    def response(_request):
        return HttpResponse("ok")

    request = rf.get("/")

    cache_middleware = CacheControlMiddleware(response)
    cached_response = cache_middleware(request)

    assert cached_response.headers["Cache-Control"] == "max-age=1800, public"


def test_existing_cache_control_is_not_overridden(rf):
    def response(_request):
        response = HttpResponse("ok")
        response.headers["Cache-Control"] = "no-store"
        return response

    request = rf.get("/")

    cache_middleware = CacheControlMiddleware(response)
    cached_response = cache_middleware(request)

    assert cached_response.headers["Cache-Control"] == "no-store"
