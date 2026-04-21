import json
import math
from pathlib import Path

from chartkick.django import LineChart


def _get_line_chart(chart_spec):
    is_multiple_series = len(chart_spec["series"]) > 1
    if is_multiple_series:
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


def get_chart(data_path):
    with Path.open(f"datagovuk/content/data/{data_path}") as data_file:
        chart_spec = json.load(data_file)
    chart_title = chart_spec["title"]
    if chart_spec["visualisation_type"] == "line":
        return _get_line_chart(chart_spec), chart_title
    return None, None
