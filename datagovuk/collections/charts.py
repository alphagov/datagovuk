import json
import math
from pathlib import Path

from chartkick.django import BarChart
from chartkick.django import LineChart
from django.template.loader import render_to_string

from datagovuk.core.utils import capture_exception


def _get_bar_chart(chart_spec):
    size = 15
    data_to_2_decimal_places = {label: f"{value:.2f}" for label, value in chart_spec["data"].items()}
    return BarChart(
        data_to_2_decimal_places,
        round=2,
        colors=["#C27A9A"],
        height="600px",
        aspectRatio=2,
        library={
            "plugins": {
                "datalabels": {
                    "display": True,
                    "anchor": "end",
                    "align": "right",
                    "offset": 3,
                    "clip": False,
                    "color": "#5D5D5D",
                    "font": {
                        "family": "Inter, sans-serif",
                        "size": size,
                        "weight": "bold",
                    },
                },
                "legend": {
                    "display": False,
                },
                "tooltip": {
                    "bodyFont": {"size": 20, "family": "Inter, sans-serif", "weight": "bold"},
                    "titleFont": {"size": 20, "family": "Inter, sans-serif", "weight": "bold"},
                },
            },
            "indexAxis": "y",
            "responsive": True,
            "maintainAspectRatio": False,
            "layout": {
                "padding": {
                    "left": 20,
                    "right": 20,
                    "top": 20,
                    "bottom": 20,
                },
            },
            "scales": {
                "x": {
                    "grid": {
                        "display": True,
                        "drawTicks": False,
                    },
                    "border": {
                        "width": 1,
                        "color": "#5D5D5D",
                        "dash": [5, 5],
                    },
                    "ticks": {
                        "display": False,
                    },
                },
                "y": {
                    "border": {
                        "width": 1,
                        "color": "#5D5D5D",
                    },
                    "ticks": {
                        "font": {"size": size, "family": "Inter, sans-serif"},
                    },
                },
            },
        },
        dataset={
            "hoverBackgroundColor": "#C27A9A",
            "backgroundColor": "#C27A9A",
            "hoverBorderColor": "#C27A9A",
            "borderWidth": 0,
        },
    )


def _get_line_chart(chart_spec):
    is_multiple_series = len(chart_spec["series"]) > 1
    point_shapes = ["circle", "triangle", "rect", "rectRot"]
    for series in chart_spec["series"]:
        data_size = len(series["data"])

        series["dataset"] = {
            "pointRadius": [0] * (data_size - 1) + [4],
            "pointStyle": [point_shapes.pop() if point_shapes else "circle"] * data_size,
        }
    return LineChart(
        chart_spec["series"],
        suffix=chart_spec.get("visualisation_suffix", ""),
        round=2,
        points=True,
        dataset={
            "empty": "No data available",
            "tension": 0.5,
            "pointRadius": 0,
            "pointHoverRadius": 10,
        },
        library={
            "plugins": {
                "datalabels": {
                    "display": False,
                },
                "legend": {
                    "display": is_multiple_series,
                    "labels": {
                        "color": "#5D5D5D",
                        "font": {
                            "size": 20,
                            "family": "Inter, sans-serif",
                            "weight": "bold",
                        },
                        "padding": 30,
                        "usePointStyle": True,
                    },
                },
                "tooltip": {
                    "bodyFont": {
                        "size": 20,
                        "family": "Inter, sans-serif",
                        "weight": "bold",
                    },
                    "titleFont": {
                        "size": 20,
                        "family": "Inter, sans-serif",
                        "weight": "bold",
                    },
                },
            },
            "responsive": True,
            "layout": {
                "padding": {
                    "top": 20,
                    "bottom": 20,
                    "left": 20,
                    "right": 20,
                },
            },
            "scales": {
                "y": {
                    "min": chart_spec.get("min_value", 0),
                    "grid": {
                        "display": True,
                    },
                    "border": {
                        "dash": [5, 5],
                    },
                    "ticks": {
                        "stepSize": math.ceil(
                            (math.ceil(chart_spec.get("max_value", 0)) * 0.25) / chart_spec.get("number_base", 1),
                        ),
                        "maxTicksLimit": 10,
                        "autoSkip": False,
                        "font": {
                            "size": 20,
                        },
                    },
                },
                "x": {
                    "border": {
                        "display": True,
                    },
                    "ticks": {
                        "font": {
                            "size": 20,
                        },
                    },
                },
            },
        },
        legend="bottom",
    )


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


def get_visualisation(data_path):
    try:
        with Path.open(f"datagovuk/content/data/{data_path}") as data_file:
            visualisation_spec = json.load(data_file)
    except FileNotFoundError as e:
        capture_exception(e)
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
    }
