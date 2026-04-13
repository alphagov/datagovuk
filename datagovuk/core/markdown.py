from pathlib import Path

import frontmatter
import mistune


class MarkdownToHTMLRenderer(mistune.HTMLRenderer):
    def link(self, text, url, title=None):
        return f'<a href="{url}" class="govuk-link datagovuk-link datagovuk-link--secondary">{text}</a>\n'

    def table(self, text):
        return f'<table class="govuk-table">\n{text}</table>\n'

    def table_head(self, text):
        return f'<thead class="govuk-table__head">{text}</thead>\n'

    def table_body(self, text):
        return f'<tbody class="govuk-table__body">{text}</tbody>\n'

    def table_row(self, text):
        return f'<tr class="govuk-table__row">{text}</tr>\n'

    def table_cell(self, text, head=False, align=None):  # noqa: FBT002
        if head:
            return f'<th class="govuk-table__header">{text}</th>\n'
        return f'<td class="govuk-table__cell">{text}</td>\n'

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

    def blockquote(self, text):
        return f'<blockquote class="govuk-inset-text datagovuk-inset-text">{text}</blockquote>\n'

    def list(self, text, ordered, depth=None):
        if ordered:
            return f'<ol class="govuk-list govuk-list--number datagovuk-list datagovuk-body">{text}</ol>\n'
        return f'<ul class="govuk-list govuk-list--bullet datagovuk-list datagovuk-body">{text}</ul>\n'

    def thematic_break(self):
        return '<hr class="datagovuk-collection-header__underline">\n'


render_markdown = mistune.create_markdown(renderer=MarkdownToHTMLRenderer())


def _transform_context(value):
    if isinstance(value, dict):
        return {key.replace("-", "_"): _transform_context(value) for key, value in value.items()}
    if isinstance(value, list):
        return [_transform_context(item) for item in value]
    return value


def get_template_context_from_markdown(markdown_file_path):
    with Path.open(markdown_file_path) as markdown_file:
        parsed_frontmatter = frontmatter.load(markdown_file)
        frontmatter_context = dict(parsed_frontmatter)
        frontmatter_context["content"] = render_markdown(parsed_frontmatter.content)
        return _transform_context(frontmatter_context)
