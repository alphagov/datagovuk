from django import forms


class SearchForm(forms.Form):
    query = forms.CharField(label="Search directory", max_length=256, required=False)
