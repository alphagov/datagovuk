import json
from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ImproperlyConfigured

from datagovuk.directory.solr import Preview, SolrDatafile, SolrDataset, get_solr_client


def test_get_solr_client_no_solr_url(settings):
    settings.SOLR_URL = None
    with pytest.raises(ImproperlyConfigured):
        get_solr_client()


@patch("datagovuk.directory.solr.pysolr")
def test_get_solr_client_solr_url_set(pysolr_mock, settings):
    settings.SOLR_URL = "http://solr.example.net"
    client = get_solr_client()
    assert client == pysolr_mock.Solr.return_value


class TestSolrDatafileModel:
    def test_solr_datafile_model_from_resource(self):
        resource = {
            "id": "e5523c1b-2133-4431-9bca-ea19c939b0a8",
            "name": "Population projections (2014-based) persons by single year of age",
            "url": "https://example.com/test.csv",
            "created": "2016-06-06T15:14:20.764117",
            "description": "ONS single year of age population projections for districts within North Yorkshire",
            "format": " .csv. ",
        }

        solr_datafile = SolrDatafile.from_resource(resource, None)
        assert solr_datafile.name == "Population projections (2014-based) persons by single year of age"
        assert solr_datafile.format == "CSV"
        assert solr_datafile.url == "https://example.com/test.csv"
        assert solr_datafile.created_at == "2016-06-06T15:14:20.764117"
        assert solr_datafile.uuid == "e5523c1b-2133-4431-9bca-ea19c939b0a8"
        assert solr_datafile.is_csv is True

    def test_solr_datafile_model_from_resource_with_dataset_created_at(self):
        resource = {
            "id": "e5523c1b-2133-4431-9bca-ea19c939b0a8",
            "name": "Population projections (2014-based) persons by single year of age",
            "url": "https://example.com/test.csv",
            "created": "",
            "description": "ONS single year of age population projections for districts within North Yorkshire",
            "format": "CSV",
        }

        solr_datafile = SolrDatafile.from_resource(resource, "2023-01-01T00:00:00Z")
        assert solr_datafile.name == "Population projections (2014-based) persons by single year of age"
        assert solr_datafile.format == "CSV"
        assert solr_datafile.url == "https://example.com/test.csv"
        assert solr_datafile.created_at == "2023-01-01T00:00:00Z"
        assert solr_datafile.uuid == "e5523c1b-2133-4431-9bca-ea19c939b0a8"
        assert solr_datafile.is_csv is True

    def test_solr_datafile_model_from_resource_with_missing_fields(self):
        resource = {
            "id": "550e8400-e29b-41d4-a716-446655440003",
            "url": "https://example.com/test.csv",
            "description": "Test description",
        }

        solr_datafile = SolrDatafile.from_resource(resource, "")
        assert solr_datafile.name == "Test description"
        assert solr_datafile.format == ""
        assert solr_datafile.url == "https://example.com/test.csv"
        assert solr_datafile.created_at == ""
        assert solr_datafile.uuid == "550e8400-e29b-41d4-a716-446655440003"
        assert solr_datafile.is_csv is False

    def test_solr_datafile_model_falls_back_to_dataset_created_at(self):
        resource = {
            "id": "550e8400-e29b-41d4-a716-446655440003",
            "name": "test.csv",
            "format": "CSV",
            "url": "https://example.com/test.csv",
        }

        dataset_created_at = "2023-06-01T00:00:00Z"
        solr_datafile = SolrDatafile.from_resource(resource, dataset_created_at)
        assert solr_datafile.created_at == "2023-06-01T00:00:00Z"

    def test_get_preview_returns_cached_preview(self):
        mock_preview = MagicMock()
        mock_preview.url = "https://example.com/test.csv"
        mock_preview.format = "CSV"
        mock_preview.exists = False

        solr_datafile = SolrDatafile(
            name="test.csv",
            url="https://example.com/test.csv",
            created_at="2023-01-01T00:00:00Z",
            format="CSV",
            uuid="550e8400-e29b-41d4-a716-446655440003",
            _preview=mock_preview,
        )

        preview = solr_datafile.get_preview()

        assert preview.url == "https://example.com/test.csv"
        assert preview.format == "CSV"
        assert preview.exists is False

    def test_get_preview_creates_preview_when_none(self):
        solr_datafile = SolrDatafile(
            name="test.csv",
            url="https://example.com/test.csv",
            created_at="2023-01-01T00:00:00Z",
            format="CSV",
            uuid="550e8400-e29b-41d4-a716-446655440003",
            _preview=None,
        )

        preview = solr_datafile.get_preview()

        assert preview.url == "https://example.com/test.csv"
        assert preview.format == "CSV"
        assert preview.exists is False

    def test_solr_datafile_instantiates_preview(self):
        solr_datafile = SolrDatafile(
            name="test.csv",
            url="https://example.com/test.csv",
            created_at="2023-01-01T00:00:00Z",
            format="CSV",
            uuid="550e8400-e29b-41d4-a716-446655440003",
            _preview=None,
        )

        preview = solr_datafile.preview

        assert preview.url == "https://example.com/test.csv"
        assert preview.format == "CSV"
        assert preview.exists is False


class TestSolrDatasetModel:
    def solr_doc(self, **overrides):
        doc = {
            "id": "420932c7-e6f8-43ea-adc5-3141f757b5cb",
            "name": "a-very-interesting-dataset",
            "title": "A very interesting dataset",
            "notes": "Lorem ipsum dolor sit amet.",
            "metadata_modified": "2017-06-30T09:08:37.040Z",
            "validated_data_dict": json.dumps({}),
        }
        doc.update(overrides)
        return doc

    def test_from_solr_doc_basic_fields(self):
        solr_dataset = SolrDataset.from_solr_doc(self.solr_doc())

        assert solr_dataset.uuid == "420932c7-e6f8-43ea-adc5-3141f757b5cb"
        assert solr_dataset.name == "a-very-interesting-dataset"
        assert solr_dataset.title == "A very interesting dataset"
        assert solr_dataset.summary == "Lorem ipsum dolor sit amet."
        assert solr_dataset.public_updated_at == "2017-06-30T09:08:37.040Z"

    def test_from_solr_doc_datafile_parsed(self):
        resources = [
            {
                "id": "aaa",
                "name": "test.csv",
                "format": "CSV",
                "url": "https://example.com/test.csv",
                "created": "2023-01-01T00:00:00Z",
            },
        ]
        solr_dataset = SolrDataset.from_solr_doc(
            self.solr_doc(validated_data_dict=json.dumps({"resources": resources})),
        )

        assert len(solr_dataset.datafiles) == 1
        datafile = solr_dataset.datafiles[0]
        assert datafile.name == "test.csv"
        assert datafile.format == "CSV"
        assert datafile.url == "https://example.com/test.csv"
        assert datafile.created_at == "2023-01-01T00:00:00Z"

    def test_from_solr_doc_datafile_created_falls_back_to_metadata_created(self):
        resources = [
            {
                "id": "aaa",
                "name": "test.csv",
                "format": "CSV",
                "url": "https://example.com/test.csv",
                "created": "",
            },
        ]
        doc = self.solr_doc(
            metadata_created="2011-10-27T13:29:52.056Z",
            validated_data_dict=json.dumps({"resources": resources}),
        )

        solr_dataset = SolrDataset.from_solr_doc(doc)

        assert len(solr_dataset.datafiles) == 1
        assert solr_dataset.datafiles[0].created_at == "2011-10-27T13:29:52.056Z"

    def test_from_solr_doc_topic_formatted_from_extras_theme_primary(self):
        solr_dataset = SolrDataset.from_solr_doc(
            self.solr_doc(**{"extras_theme-primary": "environment-and-nature"}),
        )

        assert solr_dataset.topic == "Environment and nature"

    def test_from_solr_doc_topic_empty_when_extras_theme_primary_absent(self):
        solr_dataset = SolrDataset.from_solr_doc(self.solr_doc(**{"extras_theme-primary": ""}))

        assert solr_dataset.topic == ""

    def test_from_solr_doc_licence_custom_cleaned_from_extras_licence(self):
        solr_dataset = SolrDataset.from_solr_doc(
            self.solr_doc(extras_licence='["OGL v3"]'),
        )

        assert solr_dataset.licence_custom == "OGL v3"

    def test_from_solr_doc_licence_custom_empty_when_extras_licence_absent(self):
        solr_dataset = SolrDataset.from_solr_doc(self.solr_doc())

        assert solr_dataset.licence_custom == ""

    def test_from_solr_doc_licence_fields_parsed_from_validated_data_dict(self):
        data = {
            "license_title": "UK Open Government Licence (OGL)",
            "license_url": "http://reference.data.gov.uk/id/open-government-licence",
            "license_id": "uk-ogl",
        }
        solr_dataset = SolrDataset.from_solr_doc(self.solr_doc(validated_data_dict=json.dumps(data)))

        assert solr_dataset.licence_title == "UK Open Government Licence (OGL)"
        assert solr_dataset.licence_url == "http://reference.data.gov.uk/id/open-government-licence"
        assert solr_dataset.licence_code == "uk-ogl"

    def test_from_solr_doc_contact_and_foi_fields_parsed(self):
        data = {
            "contact-email": "contact@example.com",
            "contact-name": "Contact Name",
            "foi-name": "FOI Officer",
            "foi-email": "foi@example.com",
            "foi-web": "https://example.com/foi",
        }
        solr_dataset = SolrDataset.from_solr_doc(self.solr_doc(validated_data_dict=json.dumps(data)))

        assert solr_dataset.contact_email == "contact@example.com"
        assert solr_dataset.contact_name == "Contact Name"
        assert solr_dataset.foi_name == "FOI Officer"
        assert solr_dataset.foi_email == "foi@example.com"
        assert solr_dataset.foi_web == "https://example.com/foi"

    def test_from_solr_doc_supporting_document_goes_to_docs_not_datafiles(self):
        resources = [
            {
                "id": "aaa",
                "name": "Data file",
                "format": "CSV",
                "url": "http://example.com/data.csv",
                "created": "2023-01-01T00:00:00Z",
            },
            {
                "id": "bbb",
                "name": "Supporting doc",
                "resource-type": "supporting-document",
                "format": "PDF",
                "url": "http://example.com/doc.pdf",
                "created": "2023-01-01T00:00:00Z",
            },
        ]
        doc = self.solr_doc(validated_data_dict=json.dumps({"resources": resources}))

        solr_dataset = SolrDataset.from_solr_doc(doc)

        assert len(solr_dataset.datafiles) == 1
        assert solr_dataset.datafiles[0].name == "Data file"
        assert len(solr_dataset.docs) == 1
        assert solr_dataset.docs[0]["name"] == "Supporting doc"


class TestPreviewModel:
    def test_preview_model_from_solr_datafile(self):
        preview = Preview(
            url="https://example.com/test.csv",
            format="CSV",
            exists=True,
        )

        assert preview.url == "https://example.com/test.csv"
        assert preview.format == "CSV"
        assert preview.exists is True
