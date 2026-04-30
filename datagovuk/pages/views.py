from django.conf import settings

from datagovuk.core.views import RenderedMarkdownView


class PagesView(RenderedMarkdownView):
    template_name = "pages/content_page.jinja"

    def get_markdown_file_path(self):
        return f"{settings.DATAGOVUK_CONTENT_PAGES_ROOT}{self.kwargs['slug']}.md"
