import csv
from unittest.mock import MagicMock, patch

import requests

from datagovuk.directory.preview_utils import fetch_csv, fetch_raw_content


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
    def test_falls_back_to_iso8859_on_utf8_decode_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = "café\nend".encode("iso-8859-1")
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = fetch_raw_content("http://example.com/data.csv")

        assert "caf" in result

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

    @patch("datagovuk.directory.preview_utils.csv.reader")
    @patch("datagovuk.directory.preview_utils.fetch_raw_content")
    def test_returns_empty_list_on_csv_error(self, mock_fetch, mock_reader):
        mock_fetch.return_value = "some,content"
        mock_reader.side_effect = csv.Error("bad data")

        result = fetch_csv("http://example.com/data.csv")

        assert result == []

    @patch("datagovuk.directory.preview_utils.fetch_raw_content")
    def test_skips_empty_rows(self, mock_fetch):
        mock_fetch.return_value = "name,age\n\nJohn,30"

        result = fetch_csv("http://example.com/data.csv")

        assert result == [["name", "age"], ["John", "30"]]
