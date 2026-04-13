from pathlib import Path

import frontmatter


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
        # TODO: Render markdown to HTML
        frontmatter_context["content"] = parsed_frontmatter.content
        return _transform_context(frontmatter_context)
