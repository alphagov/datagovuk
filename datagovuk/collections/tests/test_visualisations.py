import json
from pathlib import Path

import pytest

from datagovuk.collections.visualisations import Headline, get_visualisation


def test_get_visualisation_missing_file():
    visualisation = get_visualisation("missing-file.json")
    assert visualisation is None


def test_get_visualisation_bad_type(monkeypatch):
    monkeypatch.setattr(
        "datagovuk.collections.visualisations.json.load",
        lambda _: {"title": "Test", "visualisation_type": "bad-type", "series": []},
    )
    with pytest.raises(NotImplementedError):
        get_visualisation("air-quality/air-quality.json")


def test_get_visualisation_line_chart_single_series():
    visualisation = get_visualisation("air-quality/air-quality.json")

    assert visualisation["type"] == "line"
    assert (
        visualisation["title"] == "Mean number of days per urban site when air pollution was "
        "\u2018Moderate\u2019 or higher in the UK, 2010 to 2024"
    )
    options = visualisation["visualisation"]["options"]
    assert options["chart"]["type"] == "spline"
    assert options["legend"]["enabled"] is False
    assert options["xAxis"]["categories"][0] == "2010"
    # The series has no name in the JSON file, so it gets the default name
    assert options["series"][0]["name"] == "Value"


def test_get_visualisation_line_chart_multi_series():
    visualisation = get_visualisation("uk-trade/total-uk-imports-exports-2010-2025.json")

    options = visualisation["visualisation"]["options"]
    assert options["title"]["text"] == "Total UK exports and imports in goods and services"
    assert options["palette"] == {"colorScheme": "light"}
    assert options["legend"]["enabled"] is True
    # The key doesn't look clickable
    assert options["legend"]["itemStyle"]["cursor"] == "default"
    assert options["xAxis"]["categories"] == [str(year) for year in range(2010, 2026)]
    # The JSON file sets a minimum but no maximum
    assert (options["yAxis"]["min"], "max" in options["yAxis"]) == (100, False)
    # The axis ends at the first gridline above the highest value, without extra space above it
    assert options["yAxis"]["maxPadding"] == 0
    assert options["yAxis"]["labels"]["format"] == "£{value:,f}bn"
    tooltip = options["tooltip"]
    assert (tooltip["valuePrefix"], tooltip["valueSuffix"], tooltip["valueDecimals"]) == ("£", "bn", 2)
    assert tooltip["style"] == {"fontSize": "18px"}
    assert [series["name"] for series in options["series"]] == ["Value of exports", "Value of imports"]
    assert [series["color"] for series in options["series"]] == ["#C27A9A", "#00890B"]

    exports_data = options["series"][0]["data"]
    # Every point has a small marker, and the key shows each series' marker shape at full size
    assert exports_data[:2] == [{"y": 464.495, "marker": {"radius": 3}}, {"y": 522.107, "marker": {"radius": 3}}]
    assert options["plotOptions"]["spline"]["marker"] == {"enabled": True, "radius": 8}
    assert (options["legend"]["symbolWidth"], options["legend"]["symbolHeight"]) == (16, 16)
    # The latest value is highlighted with a larger marker
    assert exports_data[-1] == {"y": 925.541, "marker": {"radius": 8}}
    # Screen readers hear the series name first when a point is focused
    assert options["accessibility"]["point"]["descriptionFormat"] == (
        "{series.name}, {category}: {#if isNull}No value{else}£{y:,.2f}bn{/if}."
    )


def test_get_visualisation_line_chart_max_value():
    visualisation = get_visualisation("childhood-vaccinations/mmr1-coverage-by-nations.json")

    y_axis = visualisation["visualisation"]["options"]["yAxis"]
    assert (y_axis["min"], y_axis["max"]) == (80, 100)


def test_get_visualisation_line_chart_table():
    visualisation = get_visualisation("uk-trade/total-uk-imports-exports-2010-2025.json")

    table = visualisation["visualisation"]["table"]
    assert table["head"] == [
        {"text": "Date", "format": "text"},
        {"text": "Value of exports (£bn)", "format": "numeric"},
        {"text": "Value of imports (£bn)", "format": "numeric"},
    ]
    assert table["rows"][0] == [
        {"text": "2010", "format": "numeric"},
        {"text": "464.495", "format": "numeric"},
        {"text": "489.677", "format": "numeric"},
    ]


def test_get_visualisation_line_chart_table_without_unit_or_series_name():
    visualisation = get_visualisation("air-quality/air-quality.json")

    assert visualisation["visualisation"]["table"]["head"][1] == {"text": "Value", "format": "numeric"}


def test_get_visualisation_line_chart_single_series_accessibility():
    visualisation = get_visualisation("air-quality/air-quality.json")

    # With only one series there's no series name to announce, so Highcharts' default description is used
    assert "accessibility" not in visualisation["visualisation"]["options"]


def test_get_visualisation_line_chart_table_missing_values(monkeypatch):
    monkeypatch.setattr(
        "datagovuk.collections.visualisations.json.load",
        lambda _: {
            "title": "Test",
            "visualisation_type": "line",
            "series": [{"name": "Test series", "data": {"2010": None, "2011": 2.5}}],
        },
    )

    visualisation = get_visualisation("air-quality/air-quality.json")

    assert visualisation["visualisation"]["table"]["rows"][0][1] == {"text": "", "format": "text"}


def test_get_visualisation_bar_chart():
    visualisation = get_visualisation("election-results/vote-share.json")

    assert visualisation["type"] == "bar"
    assert visualisation["title"] == "2024 UK General Election vote share by party (%)"
    options = visualisation["visualisation"]["options"]
    assert options["chart"]["type"] == "bar"
    assert options["legend"]["enabled"] is False
    assert options["xAxis"]["categories"][:2] == ["Labour", "Conservative"]
    assert options["yAxis"]["labels"] == {"enabled": False}
    assert options["plotOptions"]["bar"]["dataLabels"]["format"] == "{y:,.2f}"
    assert options["plotOptions"]["bar"]["borderRadius"] == 0
    assert options["tooltip"]["enabled"] is False
    # 13 bars, each 32px high with a 12px gap, plus a 10px margin above and below
    assert (options["plotOptions"]["bar"]["pointWidth"], options["chart"]["height"]) == (32, 13 * 44 + 20)
    series = options["series"][0]
    assert (series["name"], series["color"]) == ("Value", "#C27A9A")
    assert series["data"][:2] == [33.7, 23.7]


def test_get_visualisation_bar_chart_whole_numbers():
    visualisation = get_visualisation("flood-alerts/flood-alerts-2011-2025.json")

    options = visualisation["visualisation"]["options"]
    # All the values are whole numbers, so they're shown without decimal places
    assert options["tooltip"]["valueDecimals"] == 0
    assert options["plotOptions"]["bar"]["dataLabels"]["format"] == "{y:,.0f}"


def test_get_visualisation_bar_chart_table():
    visualisation = get_visualisation("election-results/vote-share.json")

    table = visualisation["visualisation"]["table"]
    assert table["head"] == [{"text": "Category", "format": "text"}, {"text": "Value", "format": "numeric"}]
    assert table["rows"][0] == [{"text": "Labour", "format": "text"}, {"text": "33.7", "format": "numeric"}]


def test_get_visualisation_chart_table_thousands_separator():
    visualisation = get_visualisation("flood-alerts/flood-alerts-2011-2025.json")

    # Values have a thousands separator, but the row headings (years) don't
    first_row = visualisation["visualisation"]["table"]["rows"][0]
    assert first_row == [{"text": "2025", "format": "numeric"}, {"text": "2,931", "format": "numeric"}]


def test_get_visualisation_headline():
    visualisation = get_visualisation("get-company-information/companies-house-register-headlines.json")

    assert isinstance(visualisation["visualisation"], Headline)
    assert visualisation["type"] == "headline"
    assert visualisation["title"] == "Companies incorporated and dissolved (2024/25)"
    assert "New companies incorporated 2024/2025" in str(visualisation["visualisation"])


def test_visualisation_download_file_exists(settings):
    visualisation_files = list(Path(settings.DATAGOVUK_CONTENT_DATA_ROOT).rglob("*.json"))
    for file in visualisation_files:
        data = json.loads(file.read_text(encoding="utf-8"))
        download_file = data.get("download")
        if download_file is not None:
            csv_path = file.parent / download_file
            assert csv_path.exists()
