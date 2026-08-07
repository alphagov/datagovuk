import inspect
import textwrap

from datagovuk.core.markdown import get_template_context_from_markdown, render_markdown

# Allow long lines in this file..
# ruff: noqa: E501


class TestMarkdownToHTMLRenderer:
    def test_link(self):
        rendered_markdown = render_markdown("[Some text](https://example.net/some-path)")
        assert rendered_markdown == textwrap.dedent("""\
            <p class="govuk-body-m datagovuk-body"><a href="https://example.net/some-path" class="govuk-link datagovuk-link datagovuk-link--secondary">Some text</a></p>
        """)

    def test_heading(self):
        markdown = inspect.cleandoc("""
            # Heading 1

            para 1

            ## Heading 2

            para 2

            ### Heading 3

            para 3

            #### Heading 4

            para 4
        """)
        rendered_markdown = render_markdown(markdown)
        assert rendered_markdown == textwrap.dedent("""\
            <h1 class="govuk-heading-xl datagovuk-heading-xl">Heading 1</h1>
            <p class="govuk-body-m datagovuk-body">para 1</p>
            <h2 class="govuk-heading-l datagovuk-heading-l">Heading 2</h2>
            <p class="govuk-body-m datagovuk-body">para 2</p>
            <h3 class="govuk-heading-m datagovuk-heading-m">Heading 3</h3>
            <p class="govuk-body-m datagovuk-body">para 3</p>
            <h4 class="govuk-heading-s datagovuk-heading-s">Heading 4</h4>
            <p class="govuk-body-m datagovuk-body">para 4</p>
        """)

    def test_paragraph(self):
        markdown = inspect.cleandoc("""
            My first paragraph - wow.

            My second paragraph - woop.
        """)
        rendered_markdown = render_markdown(markdown)
        assert rendered_markdown == textwrap.dedent("""\
            <p class="govuk-body-m datagovuk-body">My first paragraph - wow.</p>
            <p class="govuk-body-m datagovuk-body">My second paragraph - woop.</p>
        """)

    def test_blockquote(self):
        markdown = inspect.cleandoc("""
            > My first paragraph - wow.
            >
            > My second paragraph - woop.
        """)
        rendered_markdown = render_markdown(markdown)
        assert rendered_markdown == textwrap.dedent("""\
            <blockquote class="govuk-inset-text datagovuk-inset-text"><p class="govuk-body-m datagovuk-body">My first paragraph - wow.</p>
            <p class="govuk-body-m datagovuk-body">My second paragraph - woop.</p>
            </blockquote>
        """)

    def test_list_ordered(self):
        markdown = inspect.cleandoc("""
            1. My first item
            1. My second item
            1. My third item
        """)
        rendered_markdown = render_markdown(markdown)
        assert rendered_markdown == textwrap.dedent("""\
            <ol class="govuk-list govuk-list--number datagovuk-list datagovuk-body"><li>My first item</li>
            <li>My second item</li>
            <li>My third item</li>
            </ol>
        """)

    def test_list_unordered(self):
        markdown = inspect.cleandoc("""
            * My first item
            * My second item
            * My third item
        """)
        rendered_markdown = render_markdown(markdown)
        assert rendered_markdown == textwrap.dedent("""\
            <ul class="govuk-list govuk-list--bullet datagovuk-list datagovuk-body"><li>My first item</li>
            <li>My second item</li>
            <li>My third item</li>
            </ul>
        """)

    def test_thematic_break(self):
        markdown = inspect.cleandoc("""
            My first item

            ---

            My second item
        """)
        rendered_markdown = render_markdown(markdown)
        assert rendered_markdown == textwrap.dedent("""\
            <p class="govuk-body-m datagovuk-body">My first item</p>
            <hr class="datagovuk-collection-header__underline">
            <p class="govuk-body-m datagovuk-body">My second item</p>
        """)

    def test_table(self):
        markdown = inspect.cleandoc("""
            | Header 1 | Header 2 |
            |----------|----------|
            | Cell 1   | Cell 2   |
            | Cell 3   | Cell 4   |
        """)
        rendered_markdown = render_markdown(markdown)
        assert rendered_markdown == textwrap.dedent("""\
            <div class="datagovuk-table-container" role="region" tabindex="0"><table class="govuk-table datagovuk-table">
            <thead class="govuk-table__head datagovuk-table__head">
            <tr class="govuk-table__row datagovuk-table__row">
            <th class="govuk-table__header datagovuk-table__header">Header 1</th>
            <th class="govuk-table__header datagovuk-table__header">Header 2</th>
            </tr>
            </thead>
            <tbody class="govuk-table__body datagovuk-table__body">
            <tr class="govuk-table__row datagovuk-table__row">
            <td class="govuk-table__cell datagovuk-table__cell">Cell 1</td>
            <td class="govuk-table__cell datagovuk-table__cell">Cell 2</td>
            </tr>
            <tr class="govuk-table__row datagovuk-table__row">
            <td class="govuk-table__cell datagovuk-table__cell">Cell 3</td>
            <td class="govuk-table__cell datagovuk-table__cell">Cell 4</td>
            </tr>
            </tbody>
            </table></div>
        """)


def test_get_template_context_from_markdown():
    context = get_template_context_from_markdown("datagovuk/core/tests/sample_markdown/sample.md")
    assert context == {
        "content": textwrap.dedent("""\
            <h1 class="govuk-heading-xl datagovuk-heading-xl">Some great content</h1>
            <p class="govuk-body-m datagovuk-body">Wow!</p>
            <ul class="govuk-list govuk-list--bullet datagovuk-list datagovuk-body"><li>A</li>
            <li>List</li>
            <li>Of</li>
            <li>Things</li>
            </ul>
        """),
        "page_last_updated": "2026-03-24",
        "title": "Some title",
        "nested_items": [
            {"name": "wow", "index": 1},
            {"name": "oof", "index": 2},
        ],
    }


def test_get_template_context_from_markdown_no_frontmatter():
    context = get_template_context_from_markdown("datagovuk/core/tests/sample_markdown/sample-no-frontmatter.md")
    assert context == {
        "content": textwrap.dedent("""\
            <h1 class="govuk-heading-xl datagovuk-heading-xl">Some great content</h1>
            <p class="govuk-body-m datagovuk-body">Wow!</p>
            <ul class="govuk-list govuk-list--bullet datagovuk-list datagovuk-body"><li>A</li>
            <li>List</li>
            <li>Of</li>
            <li>Things</li>
            </ul>
        """),
    }
