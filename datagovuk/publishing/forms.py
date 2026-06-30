from django import forms

from .models import HarvestSource, Publisher


class PublisherRegistrationForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ["name", "description"]


class HarvestSourceForm(forms.ModelForm):
    class Meta:
        model = HarvestSource
        fields = ["url", "title", "source_type", "harvest_frequency"]

    def __init__(self, *args, **kwargs):
        self.publisher = kwargs.pop("publisher")
        super().__init__(*args, **kwargs)

    def save(self, commit=True):  # noqa: FBT002
        instance = super().save(commit=False)
        instance.publisher = self.publisher

        if commit:
            instance.save()
            self.save_m2m()

        return instance
