import csv
import io
import re

import requests

HTTP_RANGE_BYTES = "bytes=0-10240"
HTTP_TIMEOUT = 5


def is_numeric(value):
    if value is None:
        return False
    match_result = bool(
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
    return match_result


def fetch_raw_content(url: str):
    connection_headers = {"Range": HTTP_RANGE_BYTES}
    try:
        response = requests.get(
            url,
            headers=connection_headers,
            timeout=HTTP_TIMEOUT,
            allow_redirects=True,
        )
        response.raise_for_status()
        try:
            raw_content = response.content.decode("utf-8")
        except UnicodeDecodeError:
            raw_content = response.content.decode("iso-8859-1")
        raw_content = raw_content.replace("\r\n", "\n").replace("\r", "\n")
        return raw_content.rpartition("\n")[0]
    except requests.RequestException, UnicodeDecodeError:
        return ""


def fetch_csv(url: str):
    raw_content = fetch_raw_content(url)

    if not raw_content:
        return []

    try:
        reader = csv.reader(io.StringIO(raw_content))
        return [row for row in reader if row]
    except csv.Error:
        return []


def build_table_data(headers, rows):
    table_rows = [
        [
            {
                "text": cell,
                "format": "numeric" if is_numeric(cell) else False,
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
                "format": "numeric" if column_is_numeric else False,
            },
        )

    return table_headings, table_rows
