import pytest
from django.core.exceptions import ImproperlyConfigured

from datagovuk.directory.solr import get_solr_client


def test_get_solr_client_no_solr_url(settings):
    settings.SOLR_URL = None
    with pytest.raises(ImproperlyConfigured):
        get_solr_client()
