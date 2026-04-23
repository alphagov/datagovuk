import pytest
from chartkick.django import BarChart
from chartkick.django import LineChart

from datagovuk.collections.visualisations import Headline
from datagovuk.collections.visualisations import get_visualisation


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

    assert isinstance(visualisation["visualisation"], LineChart)
    assert visualisation["type"] == "line"
    assert (
        visualisation["title"] == "Mean number of days per urban site when air pollution was "
        "\u2018Moderate\u2019 or higher in the UK, 2010 to 2024"
    )


def test_get_visualisation_line_chart_multi_series():
    visualisation = get_visualisation("uk-house-prices/average-house-prices.json")

    assert isinstance(visualisation["visualisation"], LineChart)
    assert visualisation["type"] == "line"
    assert visualisation["title"] == "Average house price"


def test_get_visualisation_bar_chart():
    visualisation = get_visualisation("election-results/vote-share.json")

    assert isinstance(visualisation["visualisation"], BarChart)
    assert visualisation["type"] == "bar"
    assert visualisation["title"] == "2024 Vote share by party (%)"


def test_get_visualisation_headline():
    visualisation = get_visualisation("road-traffic/road-traffic-headline.json")

    assert isinstance(visualisation["visualisation"], Headline)
    assert visualisation["type"] == "headline"
    assert visualisation["title"] == "Road traffic levels by vehicle type"
