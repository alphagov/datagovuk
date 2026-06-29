import base64
from binascii import Error as BinasciiError
from http import HTTPStatus

from django.conf import settings
from django.http import HttpResponse
from django.utils.crypto import constant_time_compare


class BasicAuthMiddleware:
    """
    Require HTTP Basic Authentication when BASIC_AUTH_USERNAME and
    BASIC_AUTH_PASSWORD are configured.

    Requests matching any path in BASIC_AUTH_EXEMPT are exempt from auth.
    Requests carrying a matching bypass header are also exempt.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.username = settings.BASIC_AUTH_USERNAME
        self.password = settings.BASIC_AUTH_PASSWORD
        self.exempt_paths = settings.BASIC_AUTH_EXEMPT
        self.bypass_header = settings.BASIC_AUTH_BYPASS

    def __call__(self, request):  # noqa: PLR0911
        if not self.username or not self.password:
            return self.get_response(request)

        # Allow exempt paths through
        for exempt_path in self.exempt_paths:
            if request.path.startswith(exempt_path):
                return self.get_response(request)

        # Allow bypass header through
        if self.bypass_header:
            header_key, header_value = self.bypass_header.split(":", 1)
            header_key = header_key.strip()
            header_value = header_value.strip()
            if request.headers.get(header_key) == header_value:
                return self.get_response(request)

        # Check HTTP Basic Auth credentials
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Basic "):
            return self._unauthorized()

        try:
            encoded_credentials = auth_header[6:].encode()
            decoded_credentials = base64.b64decode(encoded_credentials).decode()
            username, password = decoded_credentials.split(":", 1)
        except (BinasciiError, ValueError):
            return self._unauthorized()

        if constant_time_compare(username, self.username) and constant_time_compare(
            password,
            self.password,
        ):
            return self.get_response(request)

        return self._unauthorized()

    def _unauthorized(self):
        response = HttpResponse(status=401)
        response["WWW-Authenticate"] = 'Basic realm="Authentication Required"'
        return response


class CacheControlMiddleware:
    """Add a default Cache-Control header to responses"""

    def __init__(self, get_response):
        self.get_response = get_response
        self.default_cache_control = getattr(settings, "CACHE_CONTROL_DEFAULT", "max-age=1800, public")

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code != HTTPStatus.OK or settings.DEBUG:
            return response
        if not response.has_header("Cache-Control"):
            response.headers["Cache-Control"] = self.default_cache_control
        return response
