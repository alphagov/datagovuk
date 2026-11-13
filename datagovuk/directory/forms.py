from django import forms

from datagovuk.collections.constants import get_collections

from .constants import FormatChoices, TopicChoices


def _without_blank(choices):
    return [(value, label) for value, label in choices if value]


class SearchForm(forms.Form):
    query = forms.CharField(label="Search directory", max_length=256, required=False)
    collection = forms.MultipleChoiceField(label="Collection", choices=[], required=False)
    publisher = forms.MultipleChoiceField(label="Publisher", choices=[], required=False)
    topic = forms.MultipleChoiceField(label="Topic", choices=_without_blank(TopicChoices.choices), required=False)
    format = forms.MultipleChoiceField(label="Format", choices=_without_blank(FormatChoices.choices), required=False)
    open_government_licence_only = forms.BooleanField(label="Open Government Licence (OGL) only", required=False)
    include_datasets_with_no_links = forms.BooleanField(
        label="Include datasets with no links",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        publisher_choices = kwargs.pop("publisher_choices", [])
        collection_choices = kwargs.pop("collection_choices", None)
        topic_choices = kwargs.pop("topic_choices", None)
        format_choices = kwargs.pop("format_choices", None)
        super().__init__(*args, **kwargs)
        self.fields["publisher"].choices = publisher_choices
        self.fields["collection"].choices = (
            collection_choices
            if collection_choices is not None
            else [(collection["title"], collection["title"]) for collection in get_collections()]
        )
        if topic_choices is not None:
            self.fields["topic"].choices = topic_choices
        if format_choices is not None:
            self.fields["format"].choices = format_choices
