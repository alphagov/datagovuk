from django.contrib.humanize.templatetags.humanize import intcomma
from django.template import defaultfilters
from django.templatetags.static import static
from django.urls import reverse
from jinja2 import ChoiceLoader, Environment, PackageLoader, PrefixLoader, pass_environment
from jinja2.filters import do_truncate

from .feature_flags import is_feature_flag_enabled


def to_govuk_items(field_choices):
    items = []
    for value, label in field_choices:
        items.append({"text": label, "value": value})
    return items


def format_file_size(file_size):
    binary_multiplier = 1024
    for unit in ("KB", "MB", "GB"):
        file_size /= binary_multiplier
        if file_size < binary_multiplier:
            return f"{file_size:.0f} {unit}"
    return f"{file_size:.0f} GB"


@pass_environment
def split_truncate(environment, s, length=255, killwords=False, end="..."):
    """
    Uses Jinja2's built-in do_truncate under the hood and returns a tuple:
    (truncated_prefix, remainder)
    """
    if s is None or len(s) <= length:
        return s, ""

    truncated = do_truncate(environment, s, length=length, killwords=killwords, end=end)

    truncate_end = len(truncated)
    if end and truncated.endswith(end):
        truncate_end = truncate_end - len(end)

    remainder = s[truncate_end:]

    return truncated, remainder


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
    env.filters["split_truncate"] = split_truncate
    env.globals.update(
        {
            "static": static,
            "url": reverse,
            "is_feature_flag_enabled": is_feature_flag_enabled,
        },
    )
    return env
