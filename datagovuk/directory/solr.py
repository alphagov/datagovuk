import pysolr
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_solr_client():
    if not settings.SOLR_URL:
        message = "SOLR_URL was not set"
        raise ImproperlyConfigured(message)
    return pysolr.Solr(settings.SOLR_URL, always_commit=True, timeout=2)
