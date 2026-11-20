from django.db import models


class TopicChoices(models.TextChoices):
    NONE = "", ""
    BUSINESS_AND_ECONOMY = "business-and-economy", "Business and economy"
    CRIME_AND_JUSTICE = "crime-and-justice", "Crime and justice"
    DEFENCE = "defence", "Defence"
    DIGITAL_SERVICES_PERFORMANCE = (
        "digital-services-performance",
        "Digital services performance",
    )
    EDUCATION = "education", "Education"
    ENVIRONMENT = "environment", "Environment"
    GOVERNMENT = "government", "Government"
    GOVERNMENT_REFERENCE_DATA = (
        "government-reference-data",
        "Government reference data",
    )
    GOVERNMENT_SPENDING = "government-spending", "Government spending"
    HEALTH = "health", "Health"
    MAPPING = "mapping", "Mapping"
    SOCIETY = "society", "Society"
    TOWNS_AND_CITIES = "towns-and-cities", "Towns and cities"
    TRANSPORT = "transport", "Transport"


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
