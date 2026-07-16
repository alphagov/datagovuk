from unittest.mock import MagicMock, patch

import requests

from datagovuk.directory.preview_utils import (
    build_table_data,
    fetch_csv,
    fetch_raw_content,
    is_numeric,
)


class TestIsNumeric:
    def test_integer_string(self):
        assert is_numeric("42") is True

    def test_float_string(self):
        assert is_numeric("3.14") is True

    def test_negative_number(self):
        assert is_numeric("-7") is True

    def test_plain_text(self):
        assert is_numeric("hello") is False

    def test_empty_string(self):
        assert is_numeric("") is False

    def test_none(self):
        assert is_numeric(None) is False

    def test_mixed_string(self):
        assert is_numeric("12abc") is False

    def test_decimal_without_leading_zero(self):
        assert is_numeric(".5") is True

    def test_negative_decimal_without_leading_zero(self):
        assert is_numeric("-.5") is True

    def test_scientific_notation(self):
        assert is_numeric("1e3") is False

    def test_infinity(self):
        assert is_numeric("inf") is False

    def test_nan(self):
        assert is_numeric("nan") is False


class TestFetchRawContent:
    @patch("datagovuk.directory.preview_utils.requests.get")
    def test_returns_truncated_and_normalised_content(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = b"col1,col2\r\nval1,val2\r\n"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = fetch_raw_content("http://example.com/test.csv")

        assert result == "col1,col2\nval1,val2"
        assert "\r" not in result

    @patch("datagovuk.directory.preview_utils.requests.get")
    def test_returns_empty_string_on_request_error(self, mock_get):
        mock_get.side_effect = requests.RequestException("timeout")

        result = fetch_raw_content("http://example.com/data.csv")

        assert result == ""

    @patch("datagovuk.directory.preview_utils.requests.get")
    def test_request_has_range_header(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = b"a,b\n1,2\n"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        fetch_raw_content("http://example.com/data.csv")

        _, kwargs = mock_get.call_args
        assert kwargs["headers"]["Range"] == "bytes=0-10240"


class TestFetchCsv:
    @patch("datagovuk.directory.preview_utils.fetch_raw_content")
    def test_returns_parsed_rows(self, mock_fetch):
        mock_fetch.return_value = "name,age\nJohn,30\nDoe,25"

        result = fetch_csv("http://example.com/data.csv")

        assert result == [["name", "age"], ["John", "30"], ["Doe", "25"]]

    @patch("datagovuk.directory.preview_utils.fetch_raw_content")
    def test_returns_empty_list_when_no_content(self, mock_fetch):
        mock_fetch.return_value = ""

        result = fetch_csv("http://example.com/data.csv")

        assert result == []

    @patch("datagovuk.directory.preview_utils.fetch_raw_content")
    def test_skips_empty_rows(self, mock_fetch):
        mock_fetch.return_value = "name,age\n\nJohn,30"

        result = fetch_csv("http://example.com/data.csv")

        assert result == [["name", "age"], ["John", "30"]]


class TestBuildTableData:
    def test_text_columns(self):
        headers = ["name", "city"]
        rows = [["John", "London"], ["Doe", "Paris"]]

        headings, rows = build_table_data(headers, rows)

        assert headings == [
            {"text": "name", "format": False},
            {"text": "city", "format": False},
        ]

    def test_numeric_column_detection(self):
        headers = ["name", "score"]
        rows = [["John", "95"], ["Doe", "87"]]

        headings, rows = build_table_data(headers, rows)

        assert headings[0]["format"] is False
        assert headings[1]["format"] == "numeric"

    def test_row_cell_format(self):
        headers = ["label", "value"]
        rows = [["item", "42"]]

        _, rows = build_table_data(headers, rows)

        assert rows[0][0]["format"] is False
        assert rows[0][1]["format"] == "numeric"

    def test_empty_inputs(self):
        headings, rows = build_table_data([], [])

        assert headings == []
        assert rows == []

    def test_mixed_numeric_column_uses_numeric_format(self):
        headers = ["value"]
        rows = [["100"], ["not a number"]]

        headings, rows = build_table_data(headers, rows)

        assert headings[0]["format"] == "numeric"
