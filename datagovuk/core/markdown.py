import os
from pathlib import Path
from urllib.parse import urlparse

import frontmatter
import mistune
from django.conf import settings
from django.http import Http404
from django.templatetags.static import static

from datagovuk.core.utils import get_image_size


class MarkdownToHTMLRenderer(mistune.HTMLRenderer):
    def link(self, text, url, title=None):
        return f'<a href="{url}" class="govuk-link datagovuk-link datagovuk-link--secondary">{text}</a>'

    def image(self, text, url, title=None):
        # Images must be static files, given as a path relative to the static folder (e.g.
        # `images/updates/chart.png`), so they get the same hashed URLs as images in templates. External and
        # absolute URLs are rejected because our CSP would block them anyway.
        parsed_url = urlparse(url)
        if parsed_url.scheme or parsed_url.netloc or url.startswith("/"):
            error_message = f"Markdown images must be a path relative to the static folder, got: {url}"
            raise ValueError(error_message)
        width, height = get_image_size(url)
        dimensions = f' width="{width}" height="{height}"' if width else ""
        attributes = f'<img class="datagovuk-image"{dimensions} loading="lazy" '
        return super().image(text, static(url), title).replace("<img ", attributes, 1)

    def heading(self, text, level, **kwargs):
        valid_header_sizes = ["xl", "l", "m", "s"]

        start_size = "xl"
        start_size_index = valid_header_sizes.index(start_size)

        # Calculate index: starting index + (current h level - 1)
        target_index = start_size_index + (level - 1)

        header_size = "s"
        if target_index < len(valid_header_sizes):
            header_size = valid_header_sizes[target_index]

        return f'<h{level} class="govuk-heading-{header_size} datagovuk-heading-{header_size}">{text}</h{level}>\n'

    def paragraph(self, text):
        return f'<p class="govuk-body-m datagovuk-body">{text}</p>\n'

    def block_quote(self, text):
        return f'<blockquote class="govuk-inset-text datagovuk-inset-text">{text}</blockquote>\n'

    def list(self, text, ordered, depth=None, **kwargs):
        if ordered:
            return f'<ol class="govuk-list govuk-list--number datagovuk-list datagovuk-body">{text}</ol>\n'
        return f'<ul class="govuk-list govuk-list--bullet datagovuk-list datagovuk-body">{text}</ul>\n'

    def thematic_break(self):
        return '<hr class="datagovuk-collection-header__underline">\n'

    def table(self, text):
        return f'<div class="datagovuk-table-container" role="region" tabindex="0"><table class="govuk-table datagovuk-table">\n{text}</table></div>\n'  # noqa: E501

    def table_head(self, text):
        return f'<thead class="govuk-table__head datagovuk-table__head">\n<tr class="govuk-table__row datagovuk-table__row">\n{text}</tr>\n</thead>\n'  # noqa: E501

    def table_body(self, text):
        return f'<tbody class="govuk-table__body datagovuk-table__body">\n{text}</tbody>\n'

    def table_row(self, text):
        return f'<tr class="govuk-table__row datagovuk-table__row">\n{text}</tr>\n'

    def table_cell(self, text, align=None, head=False):  # noqa: FBT002
        tag = "th" if head else "td"
        classes = "govuk-table__header datagovuk-table__header" if head else "govuk-table__cell datagovuk-table__cell"

        return f'<{tag} class="{classes}">{text}</{tag}>\n'


render_markdown = mistune.create_markdown(
    renderer=MarkdownToHTMLRenderer(),
    plugins=["table"],
)


def _transform_context(value):
    """
    Recursively transform keys frontmatter kebab-case to pythonic underscores, e.g.
    my-key becomes my_key
    """
    if isinstance(value, dict):
        return {key.lower().replace("-", "_"): _transform_context(value) for key, value in value.items()}
    if isinstance(value, list):
        return [_transform_context(item) for item in value]
    return value


def get_template_context_from_markdown(markdown_file_path):
    with Path.open(markdown_file_path) as markdown_file:
        parsed_frontmatter = frontmatter.load(markdown_file)
        frontmatter_context = dict(parsed_frontmatter)
        frontmatter_context["content"] = render_markdown(parsed_frontmatter.content)
        return _transform_context(frontmatter_context)


def get_safe_markdown_path(path):
    markdown_file_path = os.path.normpath(path)
    not_found_message = "Content not found"
    # Double check that the fully normalised path is below our content directory
    if not markdown_file_path.startswith(settings.DATAGOVUK_CONTENT_ROOT):
        raise Http404(not_found_message)
    markdown_file_path = Path(markdown_file_path)
    if not markdown_file_path.exists():
        raise Http404(not_found_message)
    return markdown_file_path
