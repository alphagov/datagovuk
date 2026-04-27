from http import HTTPStatus

from django.urls import reverse


class TestMetrics:
    def test_metrics_endpoint_returns_prometheus_format(self, client):
        response = client.get(reverse("prometheus-metrics"))
        assert response.status_code == HTTPStatus.OK
        assert "text/plain" in response.headers["Content-Type"]
        assert b"# HELP" in response.content
        assert b"# TYPE" in response.content
