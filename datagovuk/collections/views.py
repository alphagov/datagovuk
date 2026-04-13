from datetime import date

from datagovuk.core.views import RenderedMarkdownView

from .constants import COLLECTIONS


class CollectionPage(RenderedMarkdownView):
    template_name = "collections/collection_page.jinja"

    def get_markdown_file_path(self):
        return (
            f"datagovuk/content/collections/{self.kwargs['collection_name']}/{self.kwargs['collection_page_name']}.md"
        )

    @property
    def collection_pages(self):
        return [
            {
                **collection_page,
                "url": f"/collections/{self.kwargs['collection_name']}/{collection_page['slug']}",
                "selected": collection_page["slug"] == self.kwargs["collection_page_name"],
            }
            for collection_page in COLLECTIONS[self.kwargs["collection_name"]]
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["slug"] = self.kwargs["collection_page_name"]
        context["collection"] = self.kwargs["collection_name"].replace("-", " ").capitalize()
        context["collection_slug"] = self.kwargs["collection_name"]
        context["page_last_updated"] = date.strptime(context["page_last_updated"], "%Y-%m-%d")
        context["collection_pages"] = self.collection_pages
        return context
