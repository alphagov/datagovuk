from http import HTTPStatus

import pytest
from django.urls import NoReverseMatch, reverse


def test_search_urls_are_present_when_search_v2_flag_is_enabled(client, set_search_v2_flag, mock_opensearch_client):
    set_search_v2_flag(enabled=True)

    assert reverse("search:search") == "/v2/search"
    assert reverse("search:dataset", kwargs={"slug": "some-dataset"}) == "/v2/dataset/some-dataset"
    assert client.get("/v2/search").status_code == HTTPStatus.OK


def test_search_urls_are_absent_when_search_v2_flag_is_disabled(client, set_search_v2_flag, mock_opensearch_client):
    set_search_v2_flag(enabled=False)

    with pytest.raises(NoReverseMatch):
        reverse("search:search")
    with pytest.raises(NoReverseMatch):
        reverse("search:dataset", kwargs={"slug": "some-dataset"})
    assert client.get("/v2/search").status_code == HTTPStatus.NOT_FOUND
    assert client.get("/v2/dataset/some-dataset").status_code == HTTPStatus.NOT_FOUND
    mock_opensearch_client.search.assert_not_called()
