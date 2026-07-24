from django import forms

from .constants import FormatChoices, TopicChoices


class SearchForm(forms.Form):
    query = forms.CharField(label="Search directory", max_length=256, required=False)
    publisher = forms.ChoiceField(label="Publisher", choices=[], required=False)
    topic = forms.ChoiceField(label="Topic", choices=TopicChoices, required=False)
    format = forms.ChoiceField(label="Format", choices=FormatChoices, required=False)
    open_government_licence_only = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        publisher_choices = kwargs.pop("publisher_choices", [])
        publisher_choices.insert(0, ["", ""])
        super().__init__(*args, **kwargs)
        self.fields["publisher"].choices = publisher_choices
