from django import forms

from .models import Publisher


class PublisherRegistrationForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ["name", "description"]
