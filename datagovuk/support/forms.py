from django import forms
from django.db import models


class SupportForm(forms.Form):
    class AboutChoices(models.TextChoices):
        WHOLE_WEBSITE = "whole_website", "The whole website"
        SPECIFIC_PAGE = "specific_page", "A specific page"

    details = forms.CharField(
        required=True,
        max_length=1200,
        label="What are the details",
    )
    name = forms.CharField(
        required=False,
        label="Your name",
    )
    email = forms.EmailField(
        required=False,
        label="Your email address",
    )
    http_referer = forms.CharField(
        required=False,
    )
