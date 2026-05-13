import base64
from http import HTTPStatus

import pytest
from django.http import HttpResponse

from datagovuk.core.middleware import BasicAuthMiddleware, CacheControlMiddleware


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


def _make_request(rf, path="/", headers=None, credentials=None):
    """Helper to build an HttpRequest with optional Basic auth credentials."""
    req_kwargs = {"path": path}
    if headers:
        for key, value in headers.items():
            req_kwargs[f"HTTP_{key.upper()}"] = value
    if credentials:
        encoded = base64.b64encode(f"{credentials[0]}:{credentials[1]}".encode()).decode()
        req_kwargs["HTTP_AUTHORIZATION"] = f"Basic {encoded}"
    return rf.get(**req_kwargs)


def _get_response(request):
    def get_resp(_req):
        return HttpResponse("ok")

    return get_resp(request)


class TestBasicAuthMiddleware:
    def test_no_credentials_settings_returns_ok(self, rf, settings):
        settings.BASIC_AUTH_USERNAME = None
        settings.BASIC_AUTH_PASSWORD = None

        request = rf.get("/")
        middleware = BasicAuthMiddleware(_get_response)
        response = middleware(request)

        assert response.status_code == HTTPStatus.OK

    def test_credentials_required_returns_unauthorized(self, rf, settings):
        settings.BASIC_AUTH_USERNAME = "user"
        settings.BASIC_AUTH_PASSWORD = "pass"  # noqa: S105

        request = rf.get("/")
        middleware = BasicAuthMiddleware(_get_response)
        response = middleware(request)

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.headers["WWW-Authenticate"] == 'Basic realm="Authentication Required"'

    def test_correct_credentials_returns_ok(self, rf, settings):
        settings.BASIC_AUTH_USERNAME = "user"
        settings.BASIC_AUTH_PASSWORD = "pass"  # noqa: S105

        request = _make_request(rf, credentials=("user", "pass"))
        middleware = BasicAuthMiddleware(_get_response)
        response = middleware(request)

        assert response.status_code == HTTPStatus.OK

    def test_wrong_username_returns_unauthorized(self, rf, settings):
        settings.BASIC_AUTH_USERNAME = "user"
        settings.BASIC_AUTH_PASSWORD = "pass"  # noqa: S105

        request = _make_request(rf, credentials=("wrong", "pass"))
        middleware = BasicAuthMiddleware(_get_response)
        response = middleware(request)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_wrong_password_returns_unauthorized(self, rf, settings):
        settings.BASIC_AUTH_USERNAME = "user"
        settings.BASIC_AUTH_PASSWORD = "pass"  # noqa: S105

        request = _make_request(rf, credentials=("user", "wrong"))
        middleware = BasicAuthMiddleware(_get_response)
        response = middleware(request)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_health_path_exempt_from_auth(self, rf, settings):
        settings.BASIC_AUTH_USERNAME = "user"
        settings.BASIC_AUTH_PASSWORD = "pass"  # noqa: S105

        request = rf.get("/health/")
        middleware = BasicAuthMiddleware(_get_response)
        response = middleware(request)

        assert response.status_code == HTTPStatus.OK

    def test_custom_exempt_paths(self, rf, settings):
        settings.BASIC_AUTH_USERNAME = "user"
        settings.BASIC_AUTH_PASSWORD = "pass"  # noqa: S105
        settings.BASIC_AUTH_EXEMPT = ["/status/", "/metrics/"]

        request = rf.get("/status/")
        middleware = BasicAuthMiddleware(_get_response)
        response = middleware(request)

        assert response.status_code == HTTPStatus.OK

    def test_default_exempt_path_not_allowed(self, rf, settings):
        settings.BASIC_AUTH_USERNAME = "user"
        settings.BASIC_AUTH_PASSWORD = "pass"  # noqa: S105

        # /status/ should require auth when default exempt is just /health/
        request = rf.get("/status/")
        middleware = BasicAuthMiddleware(_get_response)
        response = middleware(request)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_exempt_path_prefix_match(self, rf, settings):
        settings.BASIC_AUTH_USERNAME = "user"
        settings.BASIC_AUTH_PASSWORD = "pass"  # noqa: S105
        settings.BASIC_AUTH_EXEMPT = ["/health/"]

        request = rf.get("/health/foobar")
        middleware = BasicAuthMiddleware(_get_response)
        response = middleware(request)

        assert response.status_code == HTTPStatus.OK

    def test_bypass_header_allows_request(self, rf, settings):
        settings.BASIC_AUTH_USERNAME = "user"
        settings.BASIC_AUTH_PASSWORD = "pass"  # noqa: S105
        settings.BASIC_AUTH_BYPASS = "X-Internal-Token: secret123"

        request = _make_request(rf, headers={"X-Internal-Token": "secret123"})
        middleware = BasicAuthMiddleware(_get_response)
        response = middleware(request)

        assert response.status_code == HTTPStatus.OK

    def test_bypass_header_wrong_value_denied(self, rf, settings):
        settings.BASIC_AUTH_USERNAME = "user"
        settings.BASIC_AUTH_PASSWORD = "pass"  # noqa: S105
        settings.BASIC_AUTH_BYPASS = "X-Internal-Token: secret123"

        request = _make_request(rf, headers={"X-Internal-Token": "wrong-value"})
        middleware = BasicAuthMiddleware(_get_response)
        response = middleware(request)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_bypass_header_missing_key_denied(self, rf, settings):
        settings.BASIC_AUTH_USERNAME = "user"
        settings.BASIC_AUTH_PASSWORD = "pass"  # noqa: S105
        settings.BASIC_AUTH_BYPASS = "X-Internal-Token: secret123"

        request = rf.get("/")
        middleware = BasicAuthMiddleware(_get_response)
        response = middleware(request)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_bypass_header_whitespace_stripped(self, rf, settings):
        settings.BASIC_AUTH_USERNAME = "user"
        settings.BASIC_AUTH_PASSWORD = "pass"  # noqa: S105
        settings.BASIC_AUTH_BYPASS = " X-Internal-Token : secret123 "

        request = _make_request(rf, headers={"X-Internal-Token": "secret123"})
        middleware = BasicAuthMiddleware(_get_response)
        response = middleware(request)

        assert response.status_code == HTTPStatus.OK

    def test_bypass_exempt_path_still_requires_auth(self, rf, settings):
        """Health path is exempt; bypass header is not consulted for it."""
        settings.BASIC_AUTH_USERNAME = "user"
        settings.BASIC_AUTH_PASSWORD = "pass"  # noqa: S105
        settings.BASIC_AUTH_BYPASS = "X-Internal-Token: secret123"

        request = rf.get("/health/")
        middleware = BasicAuthMiddleware(_get_response)
        response = middleware(request)

        assert response.status_code == HTTPStatus.OK

    def test_invalid_authorization_header_returns_unauthorized(self, rf, settings):
        settings.BASIC_AUTH_USERNAME = "user"
        settings.BASIC_AUTH_PASSWORD = "pass"  # noqa: S105

        request = rf.get("/", HTTP_AUTHORIZATION="Basic not-valid-base64!!")
        middleware = BasicAuthMiddleware(_get_response)
        response = middleware(request)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_bearer_token_not_accepted(self, rf, settings):
        settings.BASIC_AUTH_USERNAME = "user"
        settings.BASIC_AUTH_PASSWORD = "pass"  # noqa: S105

        request = rf.get("/", HTTP_AUTHORIZATION="Bearer some-token")
        middleware = BasicAuthMiddleware(_get_response)
        response = middleware(request)

        assert response.status_code == HTTPStatus.UNAUTHORIZED
