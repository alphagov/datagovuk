from django import forms

from .constants import FormatChoices


class SearchForm(forms.Form):
    query = forms.CharField(label="Search directory", max_length=256, required=False)
    publisher = forms.CharField(label="Publisher", max_length=256, required=False)
    topic = forms.CharField(label="Topic", max_length=256, required=False)
    format = forms.ChoiceField(label="Format", choices=FormatChoices, required=False)
    open_government_licence_only = forms.BooleanField(required=False)
