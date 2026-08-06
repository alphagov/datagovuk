from datagovuk.core.jinja2 import format_file_size, sanitize_html, to_govuk_items


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


def test_sanitize_html_empty_string_returns_empty():
    assert sanitize_html("") == ""


def test_sanitize_html_none_returns_empty():
    assert sanitize_html(None) == ""


def test_sanitize_html_preserves_allowed_tags():
    result = sanitize_html("<p>Hello <b>world</b></p>")
    assert str(result) == "<p>Hello <b>world</b></p>"


def test_sanitize_html_removes_disallowed_tags():
    result = sanitize_html("<p>Hello <script>alert(1)</script></p>")
    assert str(result) == "<p>Hello </p>"


def test_sanitize_html_preserves_allowed_attributes_on_a_tag():
    result = sanitize_html('<a href="https://example.com" title="Example" target="_blank">link</a>')
    assert str(result) == '<a href="https://example.com" title="Example">link</a>'


def test_sanitize_html_removes_disallowed_attributes_on_a_tag():
    result = sanitize_html('<a href="https://example.com" onclick="alert(1)">link</a>')
    assert str(result) == '<a href="https://example.com">link</a>'


def test_sanitize_html_removes_unexpected_tags_with_attributes():
    result = sanitize_html('<span style="color:red" class="foo">text</span>')
    assert str(result) == "text"
