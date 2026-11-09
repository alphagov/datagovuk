from django import forms

from .constants import FormatChoices, TopicChoices


class SearchForm(forms.Form):
    query = forms.CharField(label="Search directory", max_length=256, required=False)
    publisher = forms.ChoiceField(label="Publisher", choices=[], required=False)
    topic = forms.ChoiceField(label="Topic", choices=TopicChoices, required=False)
    format = forms.ChoiceField(label="Format", choices=FormatChoices, required=False)
    open_government_licence_only = forms.BooleanField(label="Open Government Licence (OGL) only", required=False)
    include_datasets_with_no_links = forms.BooleanField(label="Include datasets with no links", required=False)
