"""Which icon to show next to each file format on a search result."""

ICON_FORMATS = {
    "table": ("csv", "tsv"),
    "file-spreadsheet": ("xls", "xlsx", "xlsm", "ods"),
    "file-text": ("pdf", "doc", "docx", "odt", "rtf", "txt", "ppt", "pptx", "odp"),
    "file-json": ("json", "geojson"),
    "file-code": ("html", "htlm", "htm", "xml", "gml", "kml", "rdf", "ttl", "sparql"),
    "file-archive": ("zip", "gz", "tar", "7z"),
    "map": ("shp", "gpkg", "geopackage", "geopackages", "wms", "wfs", "ogc wms", "ogc wfs", "esri rest"),
    "globe": ("api", "esri rest api", "powerbi"),
    "file-audio": ("mp3", "wav"),
    "file-video": ("avi", "mp4", "mov"),
    "image": ("jpg", "jpeg", "png", "gif", "tif", "tiff"),
}
DEFAULT_ICON = "file"

_ICON_BY_FORMAT = {file_format: icon for icon, formats in ICON_FORMATS.items() for file_format in formats}


def get_format_icon(file_format):
    """
    The icon name for a file format such as "CSV", ".pdf" or "application/gml+xml".
    Every format gets an icon: ones we don't recognise get a plain file.
    """
    value = (file_format or "").strip().lower().strip(".")
    # Media types like "application/gml+xml" or an iana URL: look at the last part, then at each "+" part
    candidates = [value, value.rsplit("/", 1)[-1], *value.rsplit("/", 1)[-1].split("+")]
    for candidate in candidates:
        icon = _ICON_BY_FORMAT.get(candidate.strip(".").strip())
        if icon:
            return icon
    return DEFAULT_ICON
