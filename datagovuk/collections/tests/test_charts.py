from chartkick.django import LineChart

from datagovuk.collections.charts import get_chart


def test_get_chart_single_series():
    chart, title = get_chart("air-quality/air-quality.json")

    assert isinstance(chart, LineChart)
    assert (
        title == "Mean number of days per urban site when air pollution was \u2018Moderate\u2019 or higher in the UK, "
        "2010 to 2024"
    )


def test_get_chart_multi_series():
    chart, title = get_chart("uk-house-prices/average-house-prices.json")

    assert isinstance(chart, LineChart)
    assert title == "Average house price"


def test_get_chart_non_line_type_returns_none(monkeypatch):
    monkeypatch.setattr(
        "datagovuk.collections.charts.json.load",
        lambda _: {"title": "Test", "visualisation_type": "bar", "series": []},
    )

    chart, title = get_chart("air-quality/air-quality.json")

    assert chart is None
    assert title is None
