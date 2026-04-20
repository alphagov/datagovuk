from datagovuk.core.views import RenderedMarkdownView


class PagesView(RenderedMarkdownView):
    template_name = "pages/content_page.jinja"

    def get_markdown_file_path(self):
        return f"datagovuk/content/content-pages/{self.kwargs['slug']}.md"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.kwargs["title"]
        return context
