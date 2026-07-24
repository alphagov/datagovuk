import logging
import re

import sentry_sdk

logger = logging.getLogger(__name__)


def capture_exception(exception):
    logger.exception(exception)
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
