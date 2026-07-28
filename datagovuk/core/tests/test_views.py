from http import HTTPStatus

import pytest
from django.http import Http404
from django.urls import reverse
from django.views.generic import TemplateView

from datagovuk.core.views import PaginationMixin, RenderedMarkdownView


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
        assert "Bad request - National Data Library" in response.content.decode()


class TestTestError403View:
    def test_view_synthetic_403(self, client):
        url = reverse("core:test_error_403")
        response = client.get(url)

        assert response.status_code == HTTPStatus.FORBIDDEN
        assert "Forbidden - National Data Library" in response.content.decode()


class TestTestError500View:
    def test_view_synthetic_500(self, client):
        url = reverse("core:test_error_500")
        with pytest.raises(KeyError):
            client.get(url)


class TestVersionView:
    def test_view_responds_correct_version(self, client, settings):
        settings.DATAGOVUK_GIT_SHA = "my-sha"
        url = reverse("core:version")
        response = client.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.content.decode() == settings.DATAGOVUK_GIT_SHA

    def test_view_no_setting_responds_none(self, client, settings):
        settings.DATAGOVUK_GIT_SHA = None
        url = reverse("core:version")
        response = client.get(url)

        assert response.status_code == HTTPStatus.OK
        assert response.content.decode() == "None"


class ConcretePaginationView(PaginationMixin, TemplateView):
    template_name = "collections/collection_page.jinja"


class TestPaginationMixin:
    def test_build_page_url_adds_page_param(self, rf):
        view = ConcretePaginationView()
        view.request = rf.get("/search?q=test", {"q": "test"})
        url = view.build_page_url(3)
        assert url == "/search?q=test&page=3"

    def test_build_page_url_overwrites_existing_page_param(self, rf):
        view = ConcretePaginationView()
        view.request = rf.get("/search?page=1", {"page": "1"})
        url = view.build_page_url(2)
        assert url == "/search?page=2"

    def test_build_page_url_preserves_other_query_params(self, rf):
        view = ConcretePaginationView()
        view.request = rf.get("/search?sort=recent&order=desc", {"sort": "recent", "order": "desc"})
        url = view.build_page_url(5)
        assert "sort=recent" in url
        assert "order=desc" in url
        assert "page=5" in url

    def testget_page_sequence_shows_all_pages_under_threshold(self):
        view = ConcretePaginationView()
        sequence = view.get_page_sequence(1, 5)
        assert sequence == [1, 2, 3, 4, 5]

    def testget_page_sequence_shows_all_pages_at_threshold(self):
        view = ConcretePaginationView()
        sequence = view.get_page_sequence(1, 6)
        assert sequence == [1, 2, 3, 4, 5, 6]

    def testget_page_sequence_shows_first_pages_and_ellipsis_when_near_start(self):
        view = ConcretePaginationView()
        sequence = view.get_page_sequence(1, 10)
        assert sequence == [1, 2, 3, 4, "ellipsis", 10]

    def testget_page_sequence_shows_first_pages_and_ellipsis_on_second_page(self):
        view = ConcretePaginationView()
        sequence = view.get_page_sequence(2, 10)
        assert sequence == [1, 2, 3, 4, "ellipsis", 10]

    def testget_page_sequence_shows_first_pages_and_ellipsis_on_third_page(self):
        view = ConcretePaginationView()
        sequence = view.get_page_sequence(3, 10)
        assert sequence == [1, 2, 3, 4, "ellipsis", 10]

    def testget_page_sequence_shows_first_pages_and_ellipsis_on_fourth_page(self):
        view = ConcretePaginationView()
        sequence = view.get_page_sequence(4, 10)
        assert sequence == [1, "ellipsis", 3, 4, 5, "ellipsis", 10]

    def testget_page_sequence_shows_ellipsis_and_neighbours_when_in_middle(self):
        view = ConcretePaginationView()
        sequence = view.get_page_sequence(5, 10)
        assert sequence == [1, "ellipsis", 4, 5, 6, "ellipsis", 10]

    def testget_page_sequence_shows_ellipsis_and_neighbours_near_end(self):
        view = ConcretePaginationView()
        sequence = view.get_page_sequence(7, 10)
        assert sequence == [1, "ellipsis", 7, 8, 9, 10]

    def testget_page_sequence_shows_last_pages_near_end(self):
        view = ConcretePaginationView()
        sequence = view.get_page_sequence(9, 10)
        assert sequence == [1, "ellipsis", 7, 8, 9, 10]

    def testget_page_sequence_shows_last_pages_on_last_page(self):
        view = ConcretePaginationView()
        sequence = view.get_page_sequence(10, 10)
        assert sequence == [1, "ellipsis", 7, 8, 9, 10]

    def testget_page_sequence_shows_single_page_when_only_one(self):
        view = ConcretePaginationView()
        sequence = view.get_page_sequence(1, 1)
        assert sequence == [1]

    def testget_page_sequence_shows_all_pages_when_two(self):
        view = ConcretePaginationView()
        sequence = view.get_page_sequence(1, 2)
        assert sequence == [1, 2]

    def testget_page_sequence_returns_empty_list_when_zero_pages(self):
        view = ConcretePaginationView()
        sequence = view.get_page_sequence(1, 0)
        assert sequence == []

    def test_get_govuk_pagination_returns_empty_dict_with_single_page(self):
        view = ConcretePaginationView()
        pagination = view.get_govuk_pagination(1, 1)
        assert pagination == {}

    def test_get_govuk_pagination_returns_empty_dict_with_zero_pages(self):
        view = ConcretePaginationView()
        pagination = view.get_govuk_pagination(1, 0)
        assert pagination == {}

    def test_get_govuk_pagination_returns_next_on_first_page(self, rf):
        view = ConcretePaginationView()
        view.request = rf.get("/search")
        pagination = view.get_govuk_pagination(1, 2)
        assert pagination == {
            "items": [
                {"number": 1, "href": "/search?page=1", "current": True},
                {"number": 2, "href": "/search?page=2"},
            ],
            "next": {"href": "/search?page=2"},
        }
        assert "previous" not in pagination

    def test_get_govuk_pagination_returns_previous_on_last_page(self, rf):
        view = ConcretePaginationView()
        view.request = rf.get("/search")
        pagination = view.get_govuk_pagination(2, 2)
        assert pagination == {
            "items": [
                {"number": 1, "href": "/search?page=1"},
                {"number": 2, "href": "/search?page=2", "current": True},
            ],
            "previous": {"href": "/search?page=1"},
        }

    def test_get_govuk_pagination_has_no_previous_on_first_page_of_many(self, rf):
        view = ConcretePaginationView()
        view.request = rf.get("/search")
        pagination = view.get_govuk_pagination(1, 10)
        assert "previous" not in pagination
        assert "next" in pagination
        assert pagination["next"]["href"] == "/search?page=2"

    def test_get_govuk_pagination_has_no_next_on_last_page(self, rf):
        view = ConcretePaginationView()
        view.request = rf.get("/search")
        pagination = view.get_govuk_pagination(10, 10)
        assert "next" not in pagination
        assert "previous" in pagination
        assert pagination["previous"]["href"] == "/search?page=9"

    def test_get_govuk_pagination_has_previous_and_next_in_middle(self, rf):
        view = ConcretePaginationView()
        view.request = rf.get("/search")
        pagination = view.get_govuk_pagination(5, 10)
        assert pagination["previous"]["href"] == "/search?page=4"
        assert pagination["next"]["href"] == "/search?page=6"

    def test_get_govuk_pagination_marks_current_page(self, rf):
        view = ConcretePaginationView()
        view.request = rf.get("/search")
        pagination = view.get_govuk_pagination(3, 10)
        current_items = [item for item in pagination["items"] if item.get("current")]
        assert len(current_items) == 1
        assert current_items[0]["number"] == 3  # noqa: PLR2004

    def test_get_govuk_pagination_preserves_query_params_in_hrefs(self, rf):
        view = ConcretePaginationView()
        view.request = rf.get("/search?sort=recent", {"sort": "recent"})
        pagination = view.get_govuk_pagination(2, 5)
        href = pagination["items"][1]["href"]
        assert "sort=recent" in href
        assert "page=2" in href

    def test_get_govuk_pagination_marks_ellipsis_items(self, rf):
        view = ConcretePaginationView()
        view.request = rf.get("/search")
        pagination = view.get_govuk_pagination(5, 10)
        ellipsis_items = [item for item in pagination["items"] if item.get("ellipsis")]
        assert len(ellipsis_items) == 2  # noqa: PLR2004
        assert all(item["ellipsis"] is True for item in ellipsis_items)
        # Ensure ellipsis items don't have other keys
        for item in ellipsis_items:
            assert set(item.keys()) == {"ellipsis"}

    def test_get_govuk_pagination_no_ellipsis_for_small_pagination(self, rf):
        view = ConcretePaginationView()
        view.request = rf.get("/search")
        pagination = view.get_govuk_pagination(3, 5)
        ellipsis_items = [item for item in pagination["items"] if item.get("ellipsis")]
        assert len(ellipsis_items) == 0
