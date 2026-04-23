from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control

from datagovuk.core.views import RenderedMarkdownView


class PagesView(RenderedMarkdownView):
    template_name = "pages/content_page.jinja"

    @method_decorator(cache_control(max_age=1800, public=True))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_markdown_file_path(self):
        return f"datagovuk/content/content-pages/{self.kwargs['slug']}.md"
