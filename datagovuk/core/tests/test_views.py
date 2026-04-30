from http import HTTPStatus

import pytest
from django.http import Http404
from django.urls import reverse

from datagovuk.core.views import RenderedMarkdownView


class ConcreteRenderedMarkdownView(RenderedMarkdownView):
    template_name = "collections/collection_page.jinja"

    def get_markdown_file_path(self):
        return "datagovuk/core/tests/sample_markdown/sample.md"


class MissingMarkdownView(RenderedMarkdownView):
    template_name = "collections/collection_page.jinja"

    def get_markdown_file_path(self):
        return "datagovuk/core/tests/sample_markdown/missing.md"


class BadPathMarkdownView(RenderedMarkdownView):
    template_name = "collections/collection_page.jinja"

    def get_markdown_file_path(self):
        return "datagovuk/core/tests/../../../sample_markdown/missing.md"


class BadSubclassMarkdownView(RenderedMarkdownView):
    template_name = "collections/collection_page.jinja"


@pytest.fixture(autouse=True)
def content_root(settings):
    settings.DATAGOVUK_CONTENT_ROOT = "datagovuk/core/tests/"


class TestRenderedMarkdownView:
    def test_view_markdown_exists(self, rf):
        request = rf.get("/some-url")
        response = ConcreteRenderedMarkdownView.as_view()(request)
        assert response.status_code == HTTPStatus.OK
        context_data = response.context_data
        context_data.pop("view")
        assert context_data == {
            "content": (
                '<h1 class="govuk-heading-xl datagovuk-heading-xl">Some great content</h1>\n'
                '<p class="govuk-body-m datagovuk-body">Wow!</p>\n'
                '<ul class="govuk-list govuk-list--bullet datagovuk-list datagovuk-body">'
                "<li>A</li>\n"
                "<li>List</li>\n"
                "<li>Of</li>\n"
                "<li>Things</li>\n"
                "</ul>\n"
            ),
            "page_last_updated": "2026-03-24",
            "title": "Some title",
            "nested_items": [
                {"name": "wow", "index": 1},
                {"name": "oof", "index": 2},
            ],
        }

    def test_view_markdown_missing(self, rf):
        request = rf.get("/some-url")
        with pytest.raises(Http404):
            MissingMarkdownView.as_view()(request)

    def test_view_subclass_missing_method(self, rf):
        request = rf.get("/some-url")
        with pytest.raises(NotImplementedError):
            BadSubclassMarkdownView.as_view()(request)

    def test_view_bad_markdown_path(self, rf):
        request = rf.get("/some-url")
        with pytest.raises(Http404):
            BadPathMarkdownView.as_view()(request)


class TestTestError400View:
    def test_view_synthetic_400(self, client):
        url = reverse("core:test_error_400")
        response = client.get(url)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert "Bad request - data.gov.uk" in response.content.decode()


class TestTestError403View:
    def test_view_synthetic_403(self, client):
        url = reverse("core:test_error_403")
        response = client.get(url)

        assert response.status_code == HTTPStatus.FORBIDDEN
        assert "Forbidden - data.gov.uk" in response.content.decode()


class TestTestError500View:
    def test_view_synthetic_500(self, client):
        url = reverse("core:test_error_500")
        with pytest.raises(KeyError):
            client.get(url)
