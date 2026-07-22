from django.db import models


class FormatChoices(models.TextChoices):
    NONE = "", ""
    CSV = "CSV", "CSV"
    ESRI_REST = "ESRI REST", "ESRI REST"
    GEOJSON = "GEOJSON", "GEOJSON"
    HTML = "HTML", "HTML"
    JSON = "JSON", "JSON"
    KML = "KML", "KML"
    PDF = "PDF", "PDF"
    SHP = "SHP", "SHP"
    WFS = "WFS", "WFS"
    WMS = "WMS", "WMS"
    XLS = "XLS", "XLS"
    XML = "XML", "XML"
    ZIP = "ZIP", "ZIP"
    OTHER = "Other", "Other"


FORMAT_MAPPINGS = {
    FormatChoices.CSV: [
        "CSV",
        ".csv",
        "csv",
        "CSV ",
        "csv.",
        ".CSV",
        "https://www.iana.org/assignments/media-types/text/csv",
    ],
    FormatChoices.ESRI_REST: ["Esri REST", "ESRI REST API"],
    FormatChoices.GEOJSON: ["GeoJSON", "geojson"],
    FormatChoices.HTML: ["HTML", "html", ".html"],
    FormatChoices.JSON: [
        "JSON",
        "json1.0",
        "json2.0",
        "https://www.iana.org/assignments/media-types/application/json",
    ],
    FormatChoices.KML: ["KML", "kml"],
    FormatChoices.PDF: ["PDF", ".pdf", "pdf"],
    FormatChoices.SHP: ["SHP"],
    FormatChoices.WFS: ["WFS", "OGC WFS", "ogc wfs", "wfs"],
    FormatChoices.WMS: ["WMS", "OGC WMS", "ogc wfs", "wms"],
    FormatChoices.XLS: ["XLS", "xls", ".xls"],
    FormatChoices.XML: ["XML"],
    FormatChoices.ZIP: [
        "ZIP",
        "Zip",
        "https://www.iana.org/assignments/media-types/application/zip",
        "zip",
        ".zip",
    ],
}
