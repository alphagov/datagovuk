from http import HTTPStatus

import pytest
from django.http import HttpResponse

from datagovuk.core.middleware import CacheControlMiddleware


class TestCacheControlMiddleware:
    def test_middleware_no_cache_control_cache_control_added(self, rf):
        def response(_request):
            return HttpResponse("ok")

        request = rf.get("/")

        cache_middleware = CacheControlMiddleware(response)
        cached_response = cache_middleware(request)

        assert cached_response.headers["Cache-Control"] == "max-age=1800, public"

    def test_middleware_cache_control_present_cache_control_not_added(self, rf):
        def response(_request):
            response = HttpResponse("ok")
            response.headers["Cache-Control"] = "no-store"
            return response

        request = rf.get("/")

        cache_middleware = CacheControlMiddleware(response)
        cached_response = cache_middleware(request)

        assert cached_response.headers["Cache-Control"] == "no-store"

    def test_middleware_cache_control_uses_setting(self, rf, settings):
        settings.CACHE_CONTROL_DEFAULT = "max-age=3600, public"

        def response(_request):
            return HttpResponse("ok")

        request = rf.get("/")

        cache_middleware = CacheControlMiddleware(response)
        cached_response = cache_middleware(request)

        assert cached_response.headers["Cache-Control"] == "max-age=3600, public"

    @pytest.mark.parametrize(
        "status_code",
        [
            HTTPStatus.INTERNAL_SERVER_ERROR,
            HTTPStatus.BAD_REQUEST,
            HTTPStatus.FORBIDDEN,
            HTTPStatus.NOT_FOUND,
        ],
    )
    def test_middleware_bad_status_code_no_cache_control_applied(self, status_code, rf, settings):
        settings.CACHE_CONTROL_DEFAULT = "max-age=3600, public"

        def response(_request):
            response = HttpResponse("error")
            response.status_code = status_code
            return response

        request = rf.get("/")

        cache_middleware = CacheControlMiddleware(response)
        cached_response = cache_middleware(request)

        assert cached_response.headers.get("Cache-Control") is None
