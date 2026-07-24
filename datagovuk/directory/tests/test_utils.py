import pytest

from datagovuk.directory.utils import format_date, format_file_size, resource_table_row_data

document_id = "12345678-1234-1234-1234-123456789abc"
document_name = "Document-Name"
resource_id = "87654321-4321-4321-4321-cba987654321"

base_resource = {
    "url": "https://example.com/resource.csv",
    "name": "Resource Name",
    "size": 2048,
    "format": " .csv. ",
    "last_modified": "2023-06-01T12:00:00",
    "created": None,
    "id": resource_id,
}


def test_returns_kb():
    assert format_file_size(1000) == "1 KB"


def test_returns_mb():
    assert format_file_size(1024 * 1024) == "1 MB"


def test_returns_gb():
    assert format_file_size(1024 * 1024 * 1024) == "1 GB"


def test_large_size_falls_through_to_gb():
    assert format_file_size(1024 * 1024 * 1024 * 1024) == "1024 GB"


def test_format_date():
    assert format_date("2023-06-01T12:00:00") == "01/06/2023"


def test_format_date_with_invalid_date():
    with pytest.raises(ValueError, match="Invalid isoformat string"):
        format_date("invalid-date")


def test_resource_table_row_data():
    row_data = resource_table_row_data(base_resource, document_id, document_name)

    assert row_data["url"] == base_resource["url"]
    assert row_data["name"] == base_resource["name"]
    assert row_data["file_size"] == "2 KB"
    assert row_data["format"] == "CSV"
    assert row_data["is_csv"] is True
    assert row_data["preview_url"] == f"/v1/dataset/{document_id}/{document_name}/datafile/{resource_id}/preview/"
    assert row_data["date"] == "01/06/2023"


def test_resource_table_row_data_with_no_last_modified():
    resource = {**base_resource, "last_modified": None, "created": "1999-01-01T12:00:00"}

    row_data = resource_table_row_data(resource, document_id, document_name)

    assert row_data["date"] == "01/01/1999"


def test_resource_table_row_data_with_no_size():
    resource = {**base_resource, "size": None}

    row_data = resource_table_row_data(resource, document_id, document_name)

    assert row_data["file_size"] is None


def test_resource_table_format_with_non_csv():
    resource = {**base_resource, "format": "pdf"}

    row_data = resource_table_row_data(resource, document_id, document_name)

    assert row_data["is_csv"] is False
    assert row_data["preview_url"] is None
