from jinja2 import Environment

from datagovuk.core.jinja2 import format_file_size, split_truncate, to_govuk_items


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


def test_split_truncate_returns_none_and_empty_string_for_none_input():
    env = Environment()  # noqa: S701
    truncated, remainder = split_truncate(env, None)
    assert truncated is None
    assert remainder == ""


def test_split_truncate_returns_input_and_empty_string_for_short_string():
    env = Environment()  # noqa: S701
    truncated, remainder = split_truncate(env, "hello")
    assert truncated == "hello"
    assert remainder == ""


def test_split_truncate_returns_input_and_empty_string_for_exact_length():
    env = Environment()  # noqa: S701
    truncated, remainder = split_truncate(env, "hello", length=5)
    assert truncated == "hello"
    assert remainder == ""


def test_split_truncate_returns_truncated_and_remainder_for_long_string():
    env = Environment()  # noqa: S701
    truncated, remainder = split_truncate(env, "hello world this is a long string", length=10)
    assert truncated == "hello..."
    assert remainder == " world this is a long string"


def test_split_truncate_with_no_end_string():
    env = Environment()  # noqa: S701
    truncated, remainder = split_truncate(env, "hello world this is long", length=10, end="")
    assert truncated == "hello"
    assert remainder == " world this is long"
