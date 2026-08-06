from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
from django.http import Http404
from django.urls import NoReverseMatch, reverse
from django.views.generic import TemplateView

from datagovuk.core.views import PaginationMixin, RenderedMarkdownView


@patch("datagovuk.core.views.get_dataset_by_legacy_name")
def test_legacy_dataset_redirect_view_redirects_to_directory(mock_get_dataset_by_legacy_name, client, settings):
    settings.FEATURE_FLAGS_ENABLED = [settings.FEATURE_FLAGS.SOLR_SEARCH.value]
    mock_dataset = MagicMock()
    mock_dataset.uuid = "11111111-1111-4111-8111-111111111111"
    mock_dataset.name = "some-dataset-name"
    mock_get_dataset_by_legacy_name.return_value = mock_dataset
    url = reverse("legacy_dataset", kwargs={"legacy_dataset_name": "some-dataset-name"})
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse(
        "directory:dataset",
        kwargs={"uuid": "11111111-1111-4111-8111-111111111111", "slug": "some-dataset-name"},
    )


@patch("datagovuk.core.views.get_dataset_by_legacy_name")
def test_legacy_dataset_redirect_view_returns_404_for_invalid_dataset(
    mock_get_dataset_by_legacy_name,
    client,
    settings,
):
    settings.FEATURE_FLAGS_ENABLED = [settings.FEATURE_FLAGS.SOLR_SEARCH.value]
    mock_get_dataset_by_legacy_name.return_value = None
    url = reverse("legacy_dataset", kwargs={"legacy_dataset_name": "invalid-dataset"})
    response = client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@patch("datagovuk.core.views.get_dataset_by_legacy_name")
def test_legacy_datafile_redirect_view_redirects_to_preview(mock_get_dataset_by_legacy_name, client, settings):
    settings.FEATURE_FLAGS_ENABLED = [settings.FEATURE_FLAGS.SOLR_SEARCH.value]
    mock_dataset = MagicMock()
    mock_dataset.uuid = "11111111-1111-1111-1111-111111111111"
    mock_dataset.name = "some-dataset-name"
    mock_dataset.datafiles = [MagicMock(uuid="22222222-2222-2222-2222-222222222222")]
    mock_get_dataset_by_legacy_name.return_value = mock_dataset
    url = reverse(
        "legacy_datafile",
        kwargs={
            "legacy_dataset_name": "some-dataset-name",
            "datafile_uuid": "22222222-2222-2222-2222-222222222222",
        },
    )
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse(
        "directory:preview",
        kwargs={
            "dataset_uuid": "11111111-1111-1111-1111-111111111111",
            "name": "some-dataset-name",
            "datafile_uuid": "22222222-2222-2222-2222-222222222222",
        },
    )


@patch("datagovuk.core.views.get_dataset_by_legacy_name")
def test_legacy_datafile_redirect_view_returns_404_for_invalid_dataset(
    mock_get_dataset_by_legacy_name,
    client,
    settings,
):
    settings.FEATURE_FLAGS_ENABLED = [settings.FEATURE_FLAGS.SOLR_SEARCH.value]
    mock_get_dataset_by_legacy_name.return_value = None
    url = reverse(
        "legacy_datafile",
        kwargs={
            "legacy_dataset_name": "invalid-dataset",
            "datafile_uuid": "22222222-2222-2222-2222-222222222222",
        },
    )
    response = client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@patch("datagovuk.core.views.get_dataset_by_legacy_name")
def test_legacy_datafile_redirect_view_returns_404_for_invalid_datafile(
    mock_get_dataset_by_legacy_name,
    client,
    settings,
):
    settings.FEATURE_FLAGS_ENABLED = [settings.FEATURE_FLAGS.SOLR_SEARCH.value]
    mock_dataset = MagicMock()
    mock_dataset.datafiles = [MagicMock(uuid="22222222-2222-2222-2222-222222222222")]
    mock_get_dataset_by_legacy_name.return_value = mock_dataset
    unknown_datafile_uuid = "11111111-1111-1111-1111-111111111111"
    url = reverse(
        "legacy_datafile",
        kwargs={
            "legacy_dataset_name": "some-dataset-name",
            "datafile_uuid": unknown_datafile_uuid,
        },
    )
    response = client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@patch("datagovuk.core.views.get_dataset_by_legacy_name")
@patch("datagovuk.core.views.redirect", side_effect=NoReverseMatch("NoReverseMatch"))
def test_legacy_datafile_redirect_view_returns_404_for_no_reverse_match(
    mock_redirect,
    mock_get_dataset_by_legacy_name,
    client,
    settings,
):
    settings.FEATURE_FLAGS_ENABLED = [settings.FEATURE_FLAGS.SOLR_SEARCH.value]
    mock_dataset = MagicMock()
    mock_dataset.uuid = "11111111-1111-1111-1111-111111111111"
    mock_dataset.name = "some-dataset-name"
    mock_dataset.datafiles = [MagicMock(uuid="22222222-2222-2222-2222-222222222222")]
    mock_get_dataset_by_legacy_name.return_value = mock_dataset
    url = reverse(
        "legacy_datafile",
        kwargs={
            "legacy_dataset_name": "some-dataset-name",
            "datafile_uuid": "22222222-2222-2222-2222-222222222222",
        },
    )
    response = client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_legacy_search_redirect_view_redirects_to_directory_search(client, settings):
    settings.FEATURE_FLAGS_ENABLED = [settings.FEATURE_FLAGS.SOLR_SEARCH.value]
    url = reverse("legacy_search")
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse("directory:search")


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
        pagination = view.get_govuk_pagination(page=1, rows_per_page=20, total_results=18)
        assert pagination == {
            "page": 1,
            "first_result_in_page": 1,
            "last_result_in_page": 18,
            "total_results": 18,
        }

    def test_get_govuk_pagination_returns_empty_dict_with_zero_pages(self):
        view = ConcretePaginationView()
        pagination = view.get_govuk_pagination(page=1, rows_per_page=20, total_results=0)
        assert pagination == {
            "page": 1,
            "first_result_in_page": None,
            "last_result_in_page": None,
            "total_results": 0,
        }

    def test_get_govuk_pagination_returns_next_on_first_page(self, rf):
        view = ConcretePaginationView()
        view.request = rf.get("/search")
        pagination = view.get_govuk_pagination(page=1, rows_per_page=20, total_results=35)
        assert pagination == {
            "page": 1,
            "first_result_in_page": 1,
            "last_result_in_page": 20,
            "total_results": 35,
            "pages": {
                "items": [
                    {"number": 1, "href": "/search?page=1", "current": True},
                    {"number": 2, "href": "/search?page=2"},
                ],
                "next": {"href": "/search?page=2"},
            },
        }
        assert "previous" not in pagination

    def test_get_govuk_pagination_returns_previous_on_last_page(self, rf):
        view = ConcretePaginationView()
        view.request = rf.get("/search")
        pagination = view.get_govuk_pagination(page=2, rows_per_page=2, total_results=4)
        assert pagination == {
            "page": 2,
            "first_result_in_page": 3,
            "last_result_in_page": 4,
            "total_results": 4,
            "pages": {
                "items": [
                    {"number": 1, "href": "/search?page=1"},
                    {"number": 2, "href": "/search?page=2", "current": True},
                ],
                "previous": {"href": "/search?page=1"},
            },
        }

    def test_get_govuk_pagination_has_no_previous_on_first_page_of_many(self, rf):
        view = ConcretePaginationView()
        view.request = rf.get("/search")
        pagination = view.get_govuk_pagination(page=1, rows_per_page=10, total_results=100)
        pages = pagination["pages"]
        assert "previous" not in pages
        assert "next" in pages
        assert pages["next"]["href"] == "/search?page=2"

    def test_get_govuk_pagination_has_no_next_on_last_page(self, rf):
        view = ConcretePaginationView()
        view.request = rf.get("/search")
        pagination = view.get_govuk_pagination(page=10, rows_per_page=10, total_results=100)
        pages = pagination["pages"]
        assert "next" not in pages
        assert "previous" in pages
        assert pages["previous"]["href"] == "/search?page=9"

    def test_get_govuk_pagination_has_previous_and_next_in_middle(self, rf):
        view = ConcretePaginationView()
        view.request = rf.get("/search")
        pagination = view.get_govuk_pagination(page=5, rows_per_page=10, total_results=100)
        assert pagination["pages"]["previous"]["href"] == "/search?page=4"
        assert pagination["pages"]["next"]["href"] == "/search?page=6"

    def test_get_govuk_pagination_marks_current_page(self, rf):
        view = ConcretePaginationView()
        view.request = rf.get("/search")
        pagination = view.get_govuk_pagination(page=3, rows_per_page=10, total_results=100)
        current_items = [item for item in pagination["pages"]["items"] if item.get("current")]
        assert len(current_items) == 1
        assert current_items[0]["number"] == 3  # noqa: PLR2004

    def test_get_govuk_pagination_preserves_query_params_in_hrefs(self, rf):
        view = ConcretePaginationView()
        view.request = rf.get("/search?sort=recent", {"sort": "recent"})
        pagination = view.get_govuk_pagination(page=2, rows_per_page=5, total_results=25)
        href = pagination["pages"]["items"][1]["href"]
        assert "sort=recent" in href
        assert "page=2" in href

    def test_get_govuk_pagination_marks_ellipsis_items(self, rf):
        view = ConcretePaginationView()
        view.request = rf.get("/search")
        pagination = view.get_govuk_pagination(page=5, rows_per_page=10, total_results=100)
        ellipsis_items = [item for item in pagination["pages"]["items"] if item.get("ellipsis")]
        assert len(ellipsis_items) == 2  # noqa: PLR2004
        assert all(item["ellipsis"] is True for item in ellipsis_items)
        # Ensure ellipsis items don't have other keys
        for item in ellipsis_items:
            assert set(item.keys()) == {"ellipsis"}

    def test_get_govuk_pagination_no_ellipsis_for_small_pagination(self, rf):
        view = ConcretePaginationView()
        view.request = rf.get("/search")
        pagination = view.get_govuk_pagination(page=3, rows_per_page=5, total_results=25)
        ellipsis_items = [item for item in pagination["pages"]["items"] if item.get("ellipsis")]
        assert len(ellipsis_items) == 0
