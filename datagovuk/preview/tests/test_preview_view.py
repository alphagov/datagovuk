import json
import uuid
from unittest.mock import MagicMock, patch

import pytest
from django.http import Http404
from django.urls import reverse

from datagovuk.preview.models import SolrDatafile
from datagovuk.preview.views.preview_view import PreviewView

HTTP_OK = 200
MAX_PREVIEW_ROWS = 4

DATASET_UUID = "e3c7ffd4-4187-46fd-a590-99e2af539058"
DATAFILE_UUID = "1b582059-39b8-4b16-b37c-3f2d24610e9f"
DATASET_NAME = "test-dataset"


def make_solr_doc(dataset_uuid=DATASET_UUID, resource_uuid=DATAFILE_UUID, resource_format="CSV"):
    resources = [
        {
            "id": resource_uuid,
            "name": "Test CSV",
            "url": "http://example.com/data.csv",
            "format": resource_format,
            "created": "2024-01-01T00:00:00",
        },
    ]

    return {
        "id": dataset_uuid,
        "name": "test-dataset",
        "title": "Test Dataset",
        "notes": "A test dataset",
        "metadata_modified": "2024-01-01T00:00:00",
        "validated_data_dict": json.dumps(
            {
                "license_title": "OGL",
                "license_url": "https://example.com/ogl",
                "license_id": "uk-ogl",
                "resources": resources,
            },
        ),
    }


def make_request(rf, dataset_uuid=DATASET_UUID, name=DATASET_NAME, datafile_uuid=DATAFILE_UUID):
    url = f"/dataset/{dataset_uuid}/{name}/datafile/{datafile_uuid}/preview/"
    request = rf.get(url)
    request.resolver_match = MagicMock()
    return request


def call_view(rf, dataset_uuid=DATASET_UUID, name=DATASET_NAME, datafile_uuid=DATAFILE_UUID):
    request = make_request(rf, dataset_uuid, name, datafile_uuid)
    return PreviewView.as_view()(
        request,
        dataset_uuid=dataset_uuid,
        name=name,
        datafile_uuid=datafile_uuid,
    )


@patch("datagovuk.preview.views.preview_view.fetch_csv")
@patch("datagovuk.preview.views.preview_view.get_solr_client")
def test_preview_renders_table(mock_solr, mock_fetch_csv, rf):
    mock_solr.return_value.search.return_value.docs = [make_solr_doc()]
    mock_fetch_csv.return_value = [
        ["name", "age"],
        ["John", "30"],
        ["Doe", "25"],
        ["Jane", "40"],
        ["Doe", "35"],
    ]

    response = call_view(rf)

    assert response.status_code == HTTP_OK
    assert response.context_data["preview_rows"] == MAX_PREVIEW_ROWS


@patch("datagovuk.preview.views.preview_view.fetch_csv")
@patch("datagovuk.preview.views.preview_view.get_solr_client")
def test_preview_limits_to_four_data_rows(mock_solr, mock_fetch_csv, rf):
    mock_solr.return_value.search.return_value.docs = [make_solr_doc()]
    mock_fetch_csv.return_value = [["col"], ["1"], ["2"], ["3"], ["4"], ["5"], ["6"]]

    response = call_view(rf)

    assert response.context_data["preview_rows"] == MAX_PREVIEW_ROWS


@patch("datagovuk.preview.views.preview_view.get_solr_client")
def test_preview_returns_404_when_dataset_not_found(mock_solr, rf):
    mock_solr.return_value.search.return_value.docs = []

    with pytest.raises(Http404):
        call_view(rf)


@patch("datagovuk.preview.views.preview_view.get_solr_client")
def test_preview_returns_404_when_resource_not_in_dataset(mock_solr, rf):
    mock_solr.return_value.search.return_value.docs = [make_solr_doc()]
    wrong_uuid = str(uuid.uuid4())

    with pytest.raises(SolrDatafile.DatafileNotFoundError):
        call_view(rf, datafile_uuid=wrong_uuid)


@patch("datagovuk.preview.views.preview_view.fetch_csv")
@patch("datagovuk.preview.views.preview_view.get_solr_client")
def test_preview_returns_404_when_csv_empty(mock_solr, mock_fetch_csv, rf):
    mock_solr.return_value.search.return_value.docs = [make_solr_doc()]
    mock_fetch_csv.return_value = []

    with pytest.raises(Http404):
        call_view(rf)


@patch("datagovuk.preview.views.preview_view.get_solr_client")
def test_preview_returns_404_when_not_csv(mock_solr, rf):
    mock_solr.return_value.search.return_value.docs = [make_solr_doc(resource_format="PDF")]

    with pytest.raises(Http404):
        call_view(rf)


@patch("datagovuk.preview.views.preview_view.fetch_csv")
@patch("datagovuk.preview.views.preview_view.get_solr_client")
def test_back_link_points_to_dataset_page(mock_solr, mock_fetch_csv, rf):
    mock_solr.return_value.search.return_value.docs = [make_solr_doc()]
    mock_fetch_csv.return_value = [["name"], ["John"]]

    response = call_view(rf)
    response.render()

    expected_url = reverse("directory:dataset", kwargs={"uuid": DATASET_UUID, "slug": "test-dataset"})
    assert expected_url in response.content.decode()
