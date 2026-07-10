from unittest.mock import patch

import pytest
from django.core.exceptions import ImproperlyConfigured

from datagovuk.directory.solr import get_solr_client


def test_get_solr_client_no_solr_url(settings):
    settings.SOLR_URL = None
    with pytest.raises(ImproperlyConfigured):
        get_solr_client()


@patch("datagovuk.directory.solr.pysolr")
def test_get_solr_client_solr_url_set(pysolr_mock, settings):
    settings.SOLR_URL = "http://solr.example.net"
    client = get_solr_client()
    assert client == pysolr_mock.Solr.return_value
