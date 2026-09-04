from django.db import models


class TopicChoices(models.TextChoices):
    NONE = "", ""
    BUSINESS_AND_ECONOMY = "Business and economy", "Business and economy"
    CRIME_AND_JUSTICE = "Crime and justice", "Crime and justice"
    DEFENCE = "Defence", "Defence"
    DIGITAL_SERVICES_PERFORMANCE = (
        "Digital services performance",
        "Digital services performance",
    )
    EDUCATION = "Education", "Education"
    ENVIRONMENT = "Environment", "Environment"
    GOVERNMENT = "Government and Parliament", "Government and Parliament"
    GOVERNMENT_REFERENCE_DATA = (
        "Government reference data",
        "Government reference data",
    )
    GOVERNMENT_SPENDING = "Government spending", "Government spending"
    HEALTH = "Health", "Health"
    MAPPING = "Mapping", "Mapping"
    SOCIETY = "Society", "Society"
    TOWNS_AND_CITIES = "Towns and cities", "Towns and cities"
    TRANSPORT = "Transport", "Transport"


# Unfortunately this odd looking mapping is necessary because of the way our
# solr instance returns facets for topics.  This is probably because the topic field
# (extras_theme-primary) does not have a solr schema - so solr is doing some term
# stemming
TOPICS = {
    TopicChoices.BUSINESS_AND_ECONOMY: ["busi", "businessandeconomi", "economi"],
    TopicChoices.CRIME_AND_JUSTICE: ["crime", "crimeandjustic", "justic"],
    TopicChoices.DEFENCE: ["defenc"],
    TopicChoices.DIGITAL_SERVICES_PERFORMANCE: [
        "digit",
        "digitalservicesperform",
        "perform",
        "servic",
    ],
    TopicChoices.EDUCATION: ["educ"],
    TopicChoices.ENVIRONMENT: ["environ"],
    TopicChoices.GOVERNMENT: ["govern"],
    TopicChoices.GOVERNMENT_REFERENCE_DATA: [
        "data",
        "governmentreferencedata",
        "refer",
    ],
    TopicChoices.GOVERNMENT_SPENDING: ["governmentspend", "spend"],
    TopicChoices.HEALTH: ["health"],
    TopicChoices.MAPPING: ["map"],
    TopicChoices.SOCIETY: ["societi"],
    TopicChoices.TOWNS_AND_CITIES: ["city", "town", "townsandc"],
    TopicChoices.TRANSPORT: ["transport"],
}


TOPICS_BY_SOLR_ALIAS = {alias: choice for choice, aliases in TOPICS.items() for alias in aliases}


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
    OTHER = "OTHER", "Other"


FORMATS = {
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

FORMATS_BY_FORMAT_VALUE = {alias: choice for choice, aliases in FORMATS.items() for alias in aliases}


STOP_WORDS = {
    "i",
    "me",
    "my",
    "myself",
    "we",
    "our",
    "ours",
    "ourselves",
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
    "he",
    "him",
    "his",
    "himself",
    "she",
    "her",
    "hers",
    "herself",
    "it",
    "its",
    "itself",
    "they",
    "them",
    "their",
    "theirs",
    "themselves",
    "what",
    "which",
    "who",
    "whom",
    "this",
    "that",
    "these",
    "those",
    "am",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "having",
    "do",
    "does",
    "did",
    "doing",
    "a",
    "an",
    "the",
    "and",
    "&",
    "but",
    "if",
    "or",
    "because",
    "as",
    "until",
    "while",
    "of",
    "at",
    "by",
    "for",
    "with",
    "about",
    "against",
    "between",
    "into",
    "through",
    "during",
    "before",
    "after",
    "above",
    "below",
    "to",
    "from",
    "up",
    "down",
    "in",
    "out",
    "on",
    "off",
    "over",
    "under",
    "again",
    "further",
    "then",
    "once",
    "here",
    "there",
    "when",
    "where",
    "why",
    "how",
    "all",
    "any",
    "both",
    "each",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "nor",
    "not",
    "only",
    "own",
    "same",
    "so",
    "than",
    "too",
    "very",
    "s",
    "t",
    "can",
    "will",
    "just",
    "don",
    "should",
    "now",
}
