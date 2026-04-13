import inspect

from datagovuk.core.markdown import render_markdown


class TestMarkdownToHTMLRenderer:
    def test_link(self):
        rendered_markdown = render_markdown("[Some text](https://example.net/some-path)")
        assert rendered_markdown == (
            '<p class="govuk-body-m datagovuk-body"><a href="https://example.net/some-path" class="govuk-link '
            'datagovuk-link datagovuk-link--secondary">Some text</a>\n'
            "</p>\n"
        )

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
        assert rendered_markdown == (
            '<h1 class="govuk-heading-xl datagovuk-heading-xl">Heading 1</h1>\n'
            '<p class="govuk-body-m datagovuk-body">para 1</p>\n'
            '<h2 class="govuk-heading-l datagovuk-heading-l">Heading 2</h2>\n'
            '<p class="govuk-body-m datagovuk-body">para 2</p>\n'
            '<h3 class="govuk-heading-m datagovuk-heading-m">Heading 3</h3>\n'
            '<p class="govuk-body-m datagovuk-body">para 3</p>\n'
            '<h4 class="govuk-heading-s datagovuk-heading-s">Heading 4</h4>\n'
            '<p class="govuk-body-m datagovuk-body">para 4</p>\n'
        )

    def test_paragraph(self):
        markdown = inspect.cleandoc("""
            My first paragraph - wow.

            My second paragraph - woop.
        """)
        rendered_markdown = render_markdown(markdown)
        assert rendered_markdown == (
            '<p class="govuk-body-m datagovuk-body">My first paragraph - wow.</p>\n'
            '<p class="govuk-body-m datagovuk-body">My second paragraph - woop.</p>\n'
        )

    def test_blockquote(self):
        markdown = inspect.cleandoc("""
            > My first paragraph - wow.
            >
            > My second paragraph - woop.
        """)
        rendered_markdown = render_markdown(markdown)
        assert rendered_markdown == (
            '<blockquote class="govuk-inset-text datagovuk-inset-text"><p class="govuk-body-m datagovuk-body">'
            "My first paragraph - wow.</p>\n"
            '<p class="govuk-body-m datagovuk-body">My second paragraph - woop.</p>\n'
            "</blockquote>\n"
        )

    def test_list_ordered(self):
        markdown = inspect.cleandoc("""
            1. My first item
            1. My second item
            1. My third item
        """)
        rendered_markdown = render_markdown(markdown)
        assert rendered_markdown == (
            '<ol class="govuk-list govuk-list--number datagovuk-list datagovuk-body"><li>My first item</li>\n'
            "<li>My second item</li>\n"
            "<li>My third item</li>\n"
            "</ol>\n"
        )

    def test_list_unordered(self):
        markdown = inspect.cleandoc("""
            * My first item
            * My second item
            * My third item
        """)
        rendered_markdown = render_markdown(markdown)
        assert rendered_markdown == (
            '<ul class="govuk-list govuk-list--bullet datagovuk-list datagovuk-body"><li>My first item</li>\n'
            "<li>My second item</li>\n"
            "<li>My third item</li>\n"
            "</ul>\n"
        )

    def test_thematic_break(self):
        markdown = inspect.cleandoc("""
            My first item

            ---

            My second item
        """)
        rendered_markdown = render_markdown(markdown)
        assert rendered_markdown == (
            '<p class="govuk-body-m datagovuk-body">My first item</p>\n'
            '<hr class="datagovuk-collection-header__underline">\n'
            '<p class="govuk-body-m datagovuk-body">My second item</p>\n'
        )
