from django.contrib.humanize.templatetags.humanize import intcomma
from django.template import defaultfilters
from django.templatetags.static import static
from django.urls import reverse
from jinja2 import ChoiceLoader, Environment, PackageLoader, PrefixLoader
from markdownify import markdownify

from .feature_flags import is_feature_flag_enabled


def to_govuk_items(field_choices):
    items = []
    for value, label in field_choices:
        items.append({"text": label, "value": value})
    return items


def format_file_size(file_size):
    file_size = int(file_size)
    binary_multiplier = 1024
    for unit in ("KB", "MB", "GB"):
        file_size /= binary_multiplier
        if file_size < binary_multiplier:
            return f"{file_size:.0f} {unit}"
    return f"{file_size:.0f} GB"


def environment(**options):
    django_loader = options.pop("loader")
    loaders = [
        django_loader,
        PrefixLoader(
            {
                "govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja"),
            },
        ),
    ]
    env = Environment(loader=ChoiceLoader(loaders), **options)  # noqa: S701

    # Add filters from https://docs.djangoproject.com/en/6.0/ref/templates/builtins/#built-in-filter-reference here
    django_filters = {
        "slugify": defaultfilters.slugify,
        "date": defaultfilters.date,
        "intcomma": intcomma,
    }
    env.filters.update(django_filters)
    env.filters["to_govuk_items"] = to_govuk_items
    env.filters["format_file_size"] = format_file_size
    env.filters["html_to_md"] = markdownify
    env.globals.update(
        {
            "static": static,
            "url": reverse,
            "is_feature_flag_enabled": is_feature_flag_enabled,
        },
    )
    return env
