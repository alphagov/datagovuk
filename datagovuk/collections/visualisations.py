import json
from pathlib import Path

from django.conf import settings
from django.template.loader import render_to_string

from datagovuk.core.utils import build_table_data, capture_exception

# Highcharts options shared by every chart. See https://api.highcharts.com/highcharts/
CHART_TEXT_COLOUR = "#666666"
CHART_LINE_COLOUR = "#d2d2d2"
CHART_GRID_COLOUR = "#d6d6d6"
CHART_LABEL_STYLE = {"color": CHART_TEXT_COLOUR, "fontSize": "18px"}
# Smaller labels for narrow charts, e.g. on mobile, so long category names aren't cut off
CHART_SMALL_LABEL_STYLE = {"fontSize": "14px"}
CHART_SMALL_MAX_WIDTH = 500
BAR_CHART_COLOUR = "#C27A9A"
BAR_CHART_BAR_HEIGHT = 32
BAR_CHART_BAR_GAP = 12
# Space above the first bar and below the last, outside the plot area
BAR_CHART_VERTICAL_MARGIN = 10
LINE_CHART_POINT_MARKER_RADIUS = 3
LINE_CHART_LATEST_MARKER_RADIUS = 8

# The first column heading of a chart's data table
LINE_CHART_TABLE_CATEGORY_HEADING = "Date"
BAR_CHART_TABLE_CATEGORY_HEADING = "Category"
# Used when a chart's series has no name in its JSON file
DEFAULT_SERIES_NAME = "Value"


def _get_chart_series(chart_spec):
    """
    Return the chart's series. Line charts list their series in the JSON file, while bar charts have a single set of
    values in `data`.
    """
    if "series" in chart_spec:
        return chart_spec["series"]
    return [{"data": chart_spec["data"], "color": BAR_CHART_COLOUR}]


def _get_value_decimals(series_list):
    """Show whole numbers without decimals, and round other numbers to 2 decimal places."""
    values = [value for series in series_list for value in series["data"].values() if value is not None]
    return 0 if all(isinstance(value, int) for value in values) else 2


def _get_base_chart_options(chart_spec):
    prefix = chart_spec.get("visualisation_prefix", "")
    suffix = chart_spec.get("visualisation_suffix", "")
    series_list = _get_chart_series(chart_spec)
    return {
        # Use the page's font rather than Highcharts' default font stack
        "chart": {"style": {"fontFamily": "inherit"}},
        # The title is shown in the page's <h2>, so Highcharts shouldn't draw it. It's kept in the options because the
        # accessibility module uses it to name the chart for screen readers.
        "title": {"text": chart_spec["title"], "floating": True, "style": {"display": "none"}},
        "credits": {"enabled": False},
        # Always use light colours. By default Highcharts follows the user's light or dark mode setting, but the rest of
        # the site is always light.
        "palette": {"colorScheme": "light"},
        # The accessibility module also uses these tooltip settings when reading points out to screen readers
        "tooltip": {
            "valuePrefix": prefix,
            "valueSuffix": suffix,
            "valueDecimals": _get_value_decimals(series_list),
            # Show the tooltip at the same size as the chart's labels, with its heading (e.g. the year) at full size
            # rather than Highcharts' default smaller size
            "style": {"fontSize": "18px"},
            "headerFormat": "<span>{ucfirst point.key}</span><br/>",
        },
        "legend": {
            "enabled": len(series_list) > 1,
            # The key only names each series. Clicking it doesn't hide or show them (see highcharts-init.js), so it
            # shouldn't look clickable. Keyboard users can still move through it with the arrow keys, which highlights
            # each series in turn, as hovering does.
            "itemStyle": {"color": CHART_TEXT_COLOUR, "fontSize": "20px", "fontWeight": "bold", "cursor": "default"},
            "itemHoverStyle": {"color": CHART_TEXT_COLOUR},
        },
        "xAxis": {
            "categories": list(series_list[0]["data"]),
            "lineColor": CHART_LINE_COLOUR,
            "tickColor": CHART_LINE_COLOUR,
            "labels": {"style": CHART_LABEL_STYLE},
        },
        "yAxis": {
            "title": {"text": None},
            "min": chart_spec.get("min_value", 0),
            "gridLineDashStyle": "Dash",
            "gridLineColor": CHART_GRID_COLOUR,
            # `{value:,f}` is the value with a thousands separator and its own decimal places, e.g. "£1,200bn".
            # Highcharts' default `{text}` leaves the separator off values under 10,000.
            "labels": {"format": f"{prefix}{{value:,f}}{suffix}", "style": CHART_LABEL_STYLE},
        },
        "responsive": {
            "rules": [
                {
                    "condition": {"maxWidth": CHART_SMALL_MAX_WIDTH},
                    "chartOptions": {
                        "xAxis": {"labels": {"style": CHART_SMALL_LABEL_STYLE}},
                        "yAxis": {"labels": {"style": CHART_SMALL_LABEL_STYLE}},
                    },
                },
            ],
        },
    }


def _get_chart_table(chart_spec, category_heading):
    """Return the chart's data as table headings and rows: one row per category and one column per series."""
    series_list = _get_chart_series(chart_spec)
    unit = (chart_spec.get("visualisation_prefix", "") + chart_spec.get("visualisation_suffix", "")).strip()
    series_names = [series.get("name", DEFAULT_SERIES_NAME) for series in series_list]
    headers = [category_heading] + [f"{name} ({unit})" if unit else name for name in series_names]
    rows = []
    for category in series_list[0]["data"]:
        values = [series["data"][category] for series in series_list]
        rows.append([category, *["" if value is None else value for value in values]])
    table_headings, table_rows = build_table_data(headers, rows)
    # The first column holds row headings (e.g. years), so keep its heading left-aligned even when they're numbers
    table_headings[0]["format"] = "text"
    # Show values with a thousands separator (e.g. "1,234.5"), keeping their decimal places. Row headings, like years,
    # are left as they are.
    for row in table_rows:
        for cell in row[1:]:
            if cell["format"] == "numeric":
                cell["text"] = f"{cell['text']:,}"
    return {"head": table_headings, "rows": table_rows}


def _get_line_chart_series(series):
    values = list(series["data"].values())
    # Mark each point with a small marker, and highlight the latest value with a larger one. Each series gets a
    # different marker shape by default.
    *earlier_values, latest_value = values
    return {
        "name": series.get("name", DEFAULT_SERIES_NAME),
        "color": series.get("color"),
        "data": [
            *[{"y": value, "marker": {"radius": LINE_CHART_POINT_MARKER_RADIUS}} for value in earlier_values],
            {"y": latest_value, "marker": {"radius": LINE_CHART_LATEST_MARKER_RADIUS}},
        ],
    }


def _get_line_chart(chart_spec):
    options = _get_base_chart_options(chart_spec)
    options["chart"]["type"] = "spline"
    if "max_value" in chart_spec:
        options["yAxis"]["max"] = chart_spec["max_value"]
    # End the axis at the first gridline above the highest value. By default Highcharts adds 5% of space above it first,
    # which can push the axis up a whole extra gridline (e.g. to £3,000 for a highest value of £2,392).
    options["yAxis"]["maxPadding"] = 0
    # Show a marker on every point, even when points are close together. The series' marker radius sets the size of the
    # marker in the key; each point sets its own, smaller size (see _get_line_chart_series).
    options["plotOptions"] = {
        "spline": {"lineWidth": 2, "marker": {"enabled": True, "radius": LINE_CHART_LATEST_MARKER_RADIUS}},
    }
    # Make room in the key for the full-size marker. The line Highcharts draws through it is hidden in _chart.scss.
    options["legend"]["symbolWidth"] = 16
    options["legend"]["symbolHeight"] = 16
    options["series"] = [_get_line_chart_series(series) for series in chart_spec["series"]]
    if len(options["series"]) > 1:
        # Screen readers announce each point when it's focused. Highcharts puts the series name at the end (e.g. "2010,
        # £464.50bn. Value of exports."), where it's easy to miss, so put it first instead.
        tooltip = options["tooltip"]
        value = f"{tooltip['valuePrefix']}{{y:,.{tooltip['valueDecimals']}f}}{tooltip['valueSuffix']}"
        options["accessibility"] = {
            "point": {
                "descriptionFormat": f"{{series.name}}, {{category}}: {{#if isNull}}No value{{else}}{value}{{/if}}.",
            },
        }

    return {"options": options, "table": _get_chart_table(chart_spec, LINE_CHART_TABLE_CATEGORY_HEADING)}


def _get_bar_chart(chart_spec):
    options = _get_base_chart_options(chart_spec)
    tooltip = options["tooltip"]
    value_format = f"{tooltip['valuePrefix']}{{y:,.{tooltip['valueDecimals']}f}}{tooltip['valueSuffix']}"
    # Each bar is already labelled with its value, so a tooltip on hover wouldn't add anything
    tooltip["enabled"] = False
    # Horizontal bars, each labelled with its value, so the value axis doesn't need labels
    options["chart"]["type"] = "bar"
    options["yAxis"]["labels"] = {"enabled": False}
    # End the axis at the longest bar rather than rounding it up to the next gridline, and leave a fixed space on the
    # right for that bar's label
    options["yAxis"]["maxPadding"] = 0
    options["yAxis"]["endOnTick"] = False
    options["chart"]["spacingRight"] = 70
    # Give every bar the same height and gap, whatever the number of bars, by making the chart tall enough for them.
    # Each bar sits in the middle of its own slot, so half the gap falls either side of it.
    bar_count = len(chart_spec["data"])
    options["chart"]["marginTop"] = BAR_CHART_VERTICAL_MARGIN
    options["chart"]["marginBottom"] = BAR_CHART_VERTICAL_MARGIN
    options["chart"]["height"] = bar_count * (BAR_CHART_BAR_HEIGHT + BAR_CHART_BAR_GAP) + 2 * BAR_CHART_VERTICAL_MARGIN
    options["plotOptions"] = {
        "bar": {
            "borderWidth": 0,
            # Square corners, rather than Highcharts' default rounded ones
            "borderRadius": 0,
            "pointWidth": BAR_CHART_BAR_HEIGHT,
            "dataLabels": {
                "enabled": True,
                "format": value_format,
                # Keep labels outside the bars, even for the longest bar, so they're always grey text on white
                "inside": False,
                "crop": False,
                "overflow": "allow",
                "style": {"color": CHART_TEXT_COLOUR, "fontSize": "18px", "fontWeight": "bold", "textOutline": "none"},
            },
        },
    }
    options["responsive"]["rules"][0]["chartOptions"]["plotOptions"] = {
        "bar": {"dataLabels": {"style": CHART_SMALL_LABEL_STYLE}},
    }
    options["series"] = [
        {"name": DEFAULT_SERIES_NAME, "color": BAR_CHART_COLOUR, "data": list(chart_spec["data"].values())},
    ]

    return {"options": options, "table": _get_chart_table(chart_spec, BAR_CHART_TABLE_CATEGORY_HEADING)}


class Headline:
    def __init__(self, data_items):
        self.data_items = data_items

    def __str__(self):
        return render_to_string(
            "collections/visualisations/headline.jinja",
            context={
                "items": self.data_items,
            },
        )


def _get_headline(visualisation_spec):
    return Headline(visualisation_spec["items"])


VISUALISATION_BUILDERS = {
    "line": _get_line_chart,
    "bar": _get_bar_chart,
    "headline": _get_headline,
}


def get_visualisation_spec(data_path):
    full_data_path = Path(f"{settings.DATAGOVUK_CONTENT_DATA_ROOT}{data_path}")
    try:
        with Path.open(full_data_path) as data_file:
            visualisation_spec = json.load(data_file)
            visualisation_spec["data_path"] = full_data_path
            return visualisation_spec
    except FileNotFoundError as e:
        capture_exception(e)
        return None


def get_visualisation(data_path):
    visualisation_spec = get_visualisation_spec(data_path)
    if not visualisation_spec:
        return None
    visualisation_title = visualisation_spec["title"]
    visualisation_type = visualisation_spec["visualisation_type"]
    try:
        visualisation_builder = VISUALISATION_BUILDERS[visualisation_type]
    except KeyError as e:
        error_message = f"Visualisation builder for type {visualisation_type} is not implemented"
        raise NotImplementedError(error_message) from e
    visualisation = visualisation_builder(visualisation_spec)
    return {
        "visualisation": visualisation,
        "type": visualisation_type,
        "title": visualisation_title,
        "download_exists": bool(visualisation_spec.get("download")),
    }
