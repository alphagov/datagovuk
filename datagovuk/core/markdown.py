import os
from pathlib import Path

import frontmatter
import mistune
from django.conf import settings
from django.http import Http404


class MarkdownToHTMLRenderer(mistune.HTMLRenderer):
    def link(self, text, url, title=None):
        return f'<a href="{url}" class="govuk-link datagovuk-link datagovuk-link--secondary">{text}</a>\n'

    def heading(self, text, level):
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

    def list(self, text, ordered, depth=None):
        if ordered:
            return f'<ol class="govuk-list govuk-list--number datagovuk-list datagovuk-body">{text}</ol>\n'
        return f'<ul class="govuk-list govuk-list--bullet datagovuk-list datagovuk-body">{text}</ul>\n'

    def thematic_break(self):
        return '<hr class="datagovuk-collection-header__underline">\n'


render_markdown = mistune.create_markdown(renderer=MarkdownToHTMLRenderer())


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
