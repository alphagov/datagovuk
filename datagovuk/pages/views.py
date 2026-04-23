from datagovuk.core.views import RenderedMarkdownView


class PagesView(RenderedMarkdownView):
    template_name = "pages/content_page.jinja"

    def get_markdown_file_path(self):
        return f"datagovuk/content/content-pages/{self.kwargs['slug']}.md"
