import logging
from unittest.mock import MagicMock

from datagovuk.core.utils import build_table_data, capture_exception, is_numeric


def test_capture_exception_no_sentry(caplog):
    with caplog.at_level(logging.DEBUG):
        capture_exception(NotImplementedError("My exception"))
    log_record = caplog.records[-1]
    assert log_record.message == "My exception"


def test_capture_exception_with_sentry(caplog, monkeypatch):
    class MockedClient:
        dsn = True

    monkeypatch.setattr(
        "datagovuk.core.utils.sentry_sdk.get_client",
        lambda: MockedClient,
    )
    mocked_capture_exception = MagicMock()
    monkeypatch.setattr(
        "datagovuk.core.utils.sentry_sdk.capture_exception",
        mocked_capture_exception,
    )
    exception = NotImplementedError("My exception")
    capture_exception(exception)
    mocked_capture_exception.assert_called_once()
    mocked_capture_exception.assert_called_with(exception)


def test_integer_string_is_numeric():
    assert is_numeric("42") is True


def test_float_string_is_numeric():
    assert is_numeric("3.14") is True


def test_negative_number_is_numeric():
    assert is_numeric("-7") is True


def test_plain_text_is_not_numeric():
    assert is_numeric("hello") is False


def test_empty_string_is_not_numeric():
    assert is_numeric("") is False


def test_none_is_not_numeric():
    assert is_numeric(None) is False


def test_mixed_string_is_not_numeric():
    assert is_numeric("12abc") is False


def test_decimal_without_leading_zero_is_numeric():
    assert is_numeric(".5") is True


def test_negative_decimal_without_leading_zero_is_numeric():
    assert is_numeric("-.5") is True


def test_scientific_notation_is_not_numeric():
    assert is_numeric("1e3") is False


def test_infinity_is_not_numeric():
    assert is_numeric("inf") is False


def test_nan_is_not_numeric():
    assert is_numeric("nan") is False


def test_text_columns():
    headers = ["name", "city"]
    rows = [["John", "London"], ["Doe", "Paris"]]

    headings, rows = build_table_data(headers, rows)

    assert headings == [
        {"text": "name", "format": "text"},
        {"text": "city", "format": "text"},
    ]


def test_numeric_column_detection():
    headers = ["name", "score"]
    rows = [["John", "95"], ["Doe", "87"]]

    headings, rows = build_table_data(headers, rows)

    assert headings[0]["format"] == "text"
    assert headings[1]["format"] == "numeric"


def test_row_cell_format():
    headers = ["label", "value"]
    rows = [["item", "42"]]

    _, rows = build_table_data(headers, rows)

    assert rows[0][0]["format"] == "text"
    assert rows[0][1]["format"] == "numeric"


def test_empty_inputs():
    headings, rows = build_table_data([], [])

    assert headings == []
    assert rows == []


def test_short_row_does_not_affect_column_format():
    headers = ["name", "score"]
    rows = [["John"], ["Doe", "87"]]

    headings, _ = build_table_data(headers, rows)

    assert headings[1]["format"] == "numeric"


def test_no_rows_headings_default_to_text():
    headings, rows = build_table_data(["name", "score"], [])

    assert rows == []
    assert headings == [
        {"text": "name", "format": "text"},
        {"text": "score", "format": "text"},
    ]


def test_mixed_numeric_column_uses_numeric_format():
    headers = ["value"]
    rows = [["100"], ["not a number"]]

    headings, rows = build_table_data(headers, rows)

    assert headings[0]["format"] == "numeric"
    assert rows[0][0]["format"] == "numeric"
    assert rows[1][0]["format"] == "text"
