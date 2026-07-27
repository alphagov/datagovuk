import csv
import io

import requests

from datagovuk.core.utils import capture_exception

HTTP_RANGE_BYTES = "bytes=0-10240"
HTTP_TIMEOUT = 5


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
    except (requests.RequestException, UnicodeDecodeError) as e:
        capture_exception(e)
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
