from django.contrib.humanize.templatetags.humanize import intcomma
from django.template import defaultfilters
from django.templatetags.static import static
from django.urls import reverse
from jinja2 import ChoiceLoader, Environment, PackageLoader, PrefixLoader

from .feature_flags import is_feature_flag_enabled


def combine(dict1, dict2):
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return dict1

    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = combine(result[key], value)
        else:
            result[key] = value
    return result


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
    env.filters["combine"] = combine
    env.globals.update(
        {
            "static": static,
            "url": reverse,
            "is_feature_flag_enabled": is_feature_flag_enabled,
        },
    )
    return env
