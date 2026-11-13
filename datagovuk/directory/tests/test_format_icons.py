from pathlib import Path

import pytest
from django.template.backends.jinja2 import Jinja2

from datagovuk.core.jinja2 import environment
from datagovuk.directory.format_icons import DEFAULT_ICON, ICON_FORMATS, get_format_icon


class TestGetFormatIcon:
    @pytest.mark.parametrize(
        ("file_format", "icon"),
        [
            ("CSV", "table"),
            ("XLS", "file-spreadsheet"),
            ("XLSX", "file-spreadsheet"),
            ("XLSM", "file-spreadsheet"),
            ("PDF", "file-text"),
            ("DOCX", "file-text"),
            ("PPT", "file-text"),
            ("JSON", "file-json"),
            ("GeoJSON", "file-json"),
            ("HTML", "file-code"),
            ("HTLM", "file-code"),
            ("XML", "file-code"),
            ("GML", "file-code"),
            ("ZIP", "file-archive"),
            ("SHP", "map"),
            ("Geopackages", "map"),
            ("WMS", "map"),
            ("OGC WFS", "map"),
            ("Esri REST", "map"),
            ("API", "globe"),
            ("ESRI REST API", "globe"),
            ("MP3", "file-audio"),
            ("AVI", "file-video"),
            ("PNG", "image"),
        ],
    )
    def test_known_formats_get_their_own_icon(self, file_format, icon):
        assert get_format_icon(file_format) == icon

    @pytest.mark.parametrize(
        ("file_format", "icon"),
        [
            (".pdf", "file-text"),
            (" csv ", "table"),
            ("application/gml+xml", "file-code"),
            ("application/json", "file-json"),
            ("https://www.iana.org/assignments/media-types/text/csv", "table"),
        ],
    )
    def test_dots_spaces_and_media_types_are_understood(self, file_format, icon):
        assert get_format_icon(file_format) == icon

    @pytest.mark.parametrize("file_format", ["application/vnd.lotus-organizer", "powerpointy", "", None])
    def test_unrecognised_formats_get_a_plain_file_icon(self, file_format):
        assert get_format_icon(file_format) == DEFAULT_ICON

    def test_every_icon_has_an_svg_file(self):
        icons_dir = Path("datagovuk/static/images/icons")

        for icon in [*ICON_FORMATS, DEFAULT_ICON]:
            assert (icons_dir / f"{icon}.svg").exists(), icon


def test_format_icon_filter_is_available_in_templates():
    env = environment(loader=Jinja2({"NAME": "x", "DIRS": [], "APP_DIRS": False, "OPTIONS": {}}).env.loader)

    assert env.filters["format_icon"]("PDF") == "file-text"
