import logging
import re
from functools import cache

import sentry_sdk
from django.contrib.staticfiles import finders
from django.core.files.images import get_image_dimensions

logger = logging.getLogger(__name__)


def capture_exception(exception, *, send_to_sentry=True):
    logger.error(exception, exc_info=True)
    if not send_to_sentry:
        return
    is_sentry_initialised = bool(sentry_sdk.get_client().dsn)
    if is_sentry_initialised:
        sentry_sdk.capture_exception(exception)


def build_table_data(headers, rows):
    table_rows = [
        [
            {
                "text": cell,
                "format": "numeric" if is_numeric(cell) else "text",
            }
            for cell in row
        ]
        for row in rows
    ]

    table_headings = []
    for col_index, col_name in enumerate(headers):
        column_is_numeric = any(row[col_index]["format"] == "numeric" for row in table_rows if col_index < len(row))
        table_headings.append(
            {
                "text": col_name,
                "format": "numeric" if column_is_numeric else "text",
            },
        )

    return table_headings, table_rows


def is_numeric(value):
    if value is None:
        return False
    return bool(
        re.compile(
            r"""
                ^
                -?          # optional negative sign
                (
                \d+(\.\d+)?  # digits, optionally followed by decimal
                |
                \.\d+        # or decimal point followed by digits
                )
                $
            """,
            re.VERBOSE,
        ).match(str(value)),
    )


@cache
def get_image_size(path):
    """
    Return the (width, height) of an image in the static folder, given its path relative to that folder.

    Returns (None, None) for formats that can't be read (e.g. SVG). Raises ValueError if the file doesn't exist,
    so that typos in content are caught early rather than producing a broken image.
    """
    absolute_path = finders.find(path)
    if absolute_path is None:
        error_message = f"Image not found in static files: {path}"
        raise ValueError(error_message)
    return get_image_dimensions(absolute_path)
