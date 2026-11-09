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
    GOVERNMENT = "Government", "Government"
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
