import re

import nh3
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template import defaultfilters
from django.templatetags.static import static
from django.urls import reverse
from jinja2 import ChoiceLoader, Environment, PackageLoader, PrefixLoader
from markdownify import markdownify
from markupsafe import Markup

from .feature_flags import is_feature_flag_enabled
from .markdown import render_markdown


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


def sanitize_html(value):
    """
    Sanitizes HTML string to allow only specific tags and attributes.
    Returns a Markup object so Jinja treats the result as safe HTML.
    """
    if not value:
        return ""

    allowed_tags = {"p", "b", "i", "strong", "em", "a", "ul", "ol", "li", "br", "h1", "h2", "h3", "h4", "h5", "h6"}
    allowed_attributes = {
        "a": {"href", "title", "target"},
    }

    cleaned_html = nh3.clean(
        value,
        tags=allowed_tags,
        attributes=allowed_attributes,
        link_rel=None,
    )

    return Markup(cleaned_html)  # noqa: S704


def strip_markdown(text):
    """
    Strips markdown syntax from a given text string.
    """
    if not text:
        return ""
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)  # Images
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)  # Links
    text = re.sub(r"`{1,3}(.*?)`{1,3}", r"\1", text)  # Inline code & code blocks
    text = re.sub(r"^\s*[\*+-]\s+", "", text, flags=re.MULTILINE)  # Bullet lists
    text = re.sub(r"#{1,6}\s*", "", text)  # Headers
    text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", text)  # Bold
    text = re.sub(r"(\*|_)(.*?)\1", r"\2", text)  # Italics
    return text.strip()


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
    env.filters["html_to_markdown"] = markdownify
    env.filters["markdown_to_html"] = lambda markdown: Markup(render_markdown(markdown))  # noqa: S704
    env.filters["sanitize_html"] = sanitize_html
    env.filters["strip_markdown"] = strip_markdown
    env.globals.update(
        {
            "static": static,
            "url": reverse,
            "is_feature_flag_enabled": is_feature_flag_enabled,
        },
    )
    return env
