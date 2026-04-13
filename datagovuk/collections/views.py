from datetime import date

from datagovuk.core.views import RenderedMarkdownView


class CollectionPage(RenderedMarkdownView):
    template_name = "collections/collection_page.jinja"

    def get_markdown_file_path(self):
        return (
            f"datagovuk/content/collections/{self.kwargs['collection_name']}/{self.kwargs['collection_page_name']}.md"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["slug"] = self.kwargs["collection_page_name"]
        context["collection"] = self.kwargs["collection_name"].replace("-", " ").capitalize()
        context["collection_slug"] = self.kwargs["collection_name"]
        context["page_last_updated"] = date.strptime(context["page_last_updated"], "%Y-%m-%d")
        return context
