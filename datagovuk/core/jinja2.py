from django.contrib.humanize.templatetags.humanize import intcomma
from django.template import defaultfilters
from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment


def environment(**options):
    env = Environment(**options)  # noqa: S701

    # Add filters from https://docs.djangoproject.com/en/6.0/ref/templates/builtins/#built-in-filter-reference here
    django_filters = {
        "slugify": defaultfilters.slugify,
        "date": defaultfilters.date,
        "intcomma": intcomma,
    }
    env.filters.update(django_filters)
    env.globals.update(
        {
            "static": static,
            "url": reverse,
        },
    )
    return env
