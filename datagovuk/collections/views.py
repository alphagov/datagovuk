from datetime import date

from django.urls import reverse
from django.views.generic.base import RedirectView

from datagovuk.core.views import RenderedMarkdownView

from .constants import COLLECTIONS


class CollectionPageView(RenderedMarkdownView):
    template_name = "collections/collection_page.jinja"

    def get_markdown_file_path(self):
        return (
            f"datagovuk/content/collections/{self.kwargs['collection_name']}/{self.kwargs['collection_page_name']}.md"
        )

    @property
    def collection_pages(self):
        collection_pages = []
        selected_index = 0
        for index, collection_page in enumerate(COLLECTIONS[self.kwargs["collection_name"]]):
            is_selected = collection_page["slug"] == self.kwargs["collection_page_name"]
            collection_pages.append(
                {
                    **collection_page,
                    "url": f"/collections/{self.kwargs['collection_name']}/{collection_page['slug']}",
                    "selected": is_selected,
                },
            )
            if is_selected:
                selected_index = index
        return collection_pages, selected_index

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["slug"] = self.kwargs["collection_page_name"]
        context["collection"] = self.kwargs["collection_name"].replace("-", " ").capitalize()
        context["collection_slug"] = self.kwargs["collection_name"]
        context["page_last_updated"] = date.strptime(context["page_last_updated"], "%Y-%m-%d")
        collection_pages, selected_index = self.collection_pages
        if selected_index > 0:
            context["previous_page"] = collection_pages[selected_index - 1]
        if selected_index < len(collection_pages) - 1:
            context["next_page"] = collection_pages[selected_index + 1]
        context["collection_pages"] = collection_pages
        return context


class CollectionView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        collection_name = self.kwargs["collection_name"]
        collection_page_name = COLLECTIONS[collection_name][0]["slug"]
        return reverse(
            "collections:page",
            kwargs={
                "collection_name": self.kwargs["collection_name"],
                "collection_page_name": collection_page_name,
            },
        )
