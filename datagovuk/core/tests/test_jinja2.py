from datagovuk.core.jinja2 import format_file_size, to_govuk_items


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
