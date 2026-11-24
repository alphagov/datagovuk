from django import forms

from .constants import FormatChoices, TopicChoices


class UppercaseChoiceField(forms.ChoiceField):
    """
    Choice field for values the search index holds lowercased (e.g. facet formats), so `csv` matches the `CSV` choice.
    """

    def to_python(self, value):
        return super().to_python(value).upper()


class SearchForm(forms.Form):
    query = forms.CharField(label="Search directory", max_length=256, required=False)
    publisher = forms.SlugField(label="Publisher", required=False)  # TODO: Make in to choicefield
    topic = forms.ChoiceField(label="Topic", choices=TopicChoices, required=False)
    format = UppercaseChoiceField(label="Format", choices=FormatChoices, required=False)
    open_government_licence_only = forms.BooleanField(label="Open Government Licence (OGL) only", required=False)
    include_datasets_with_no_links = forms.BooleanField(label="Include datasets with no links", required=False)
