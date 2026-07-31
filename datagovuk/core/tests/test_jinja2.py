from datagovuk.core.jinja2 import format_file_size, parse_isodate, to_govuk_items


def test_to_govuk_items_returns_items_list():
    choices = [("value", "Label"), ("value-2", "Label 2")]
    items = to_govuk_items(choices)
    assert items == [
        {"text": "Label", "value": "value"},
        {"text": "Label 2", "value": "value-2"},
    ]


def test_format_file_size_returns_kb():
    assert format_file_size(1000) == "1 KB"


def test_format_file_size_returns_mb():
    assert format_file_size(1024 * 1024) == "1 MB"


def test_format_file_size_returns_gb():
    assert format_file_size(1024 * 1024 * 1024) == "1 GB"


def test_format_file_size_large_size_falls_through_to_gb():
    assert format_file_size(1024 * 1024 * 1024 * 1024) == "1024 GB"

def test_parse_isodate_returns_datetime_for_valid_iso_string():
    result = parse_isodate("2011-11-04T00:05:23.12345Z")
    assert result == datetime(2011, 11, 4, 0, 5, 23, 123450, tzinfo=UTC)


def test_parse_isodate_returns_none_for_empty_string():
    assert parse_isodate("") is None


def test_parse_isodate_returns_none_for_none():
    assert parse_isodate(None) is None


def test_parse_isodate_returns_none_for_invalid_value():
    assert parse_isodate("not-a-date") is None
