from django import forms

from .constants import FormatChoices, TopicChoices


class SearchForm(forms.Form):
    query = forms.CharField(label="Search directory", max_length=256, required=False)
    publisher = forms.ChoiceField(label="Publisher", choices=[], required=False)
    topic = forms.ChoiceField(label="Topic", choices=TopicChoices, required=False)
    format = forms.ChoiceField(label="Format", choices=FormatChoices, required=False)
    open_government_licence_only = forms.BooleanField(label="Open Government Licence (OGL) only", required=False)
    include_datasets_with_no_links = forms.BooleanField(label="Include datasets with no links", required=False)

    def __init__(self, *args, **kwargs):
        publisher_choices = kwargs.pop("publisher_choices", [])
        publisher_choices.insert(0, ["", ""])
        topic_choices = kwargs.pop("topic_choices", None)
        format_choices = kwargs.pop("format_choices", None)
        super().__init__(*args, **kwargs)
        self.fields["publisher"].choices = publisher_choices
        if topic_choices is not None:
            topic_choices.insert(0, ["", ""])
            self.fields["topic"].choices = topic_choices
        if format_choices is not None:
            format_choices.insert(0, ["", ""])
            self.fields["format"].choices = format_choices
