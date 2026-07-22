from django import forms


class SearchForm(forms.Form):
    query = forms.CharField(label="Search directory", max_length=256)
    publisher = forms.CharField(label="Publisher", max_length=256, required=False)
    topic = forms.CharField(label="Topic", max_length=256, required=False)
    format = forms.CharField(label="Format", max_length=50, required=False)
    open_government_licence_only = forms.BooleanField(required=False)
