from datetime import date

from django.conf import settings
from django.http import FileResponse, Http404
from django.urls import reverse
from django.views.generic.base import RedirectView, View

from datagovuk.core.markdown import get_safe_markdown_path, get_template_context_from_markdown
from datagovuk.core.views import RenderedMarkdownView

from .constants import COLLECTIONS, COLLECTIONS_BY_SLUG
from .visualisations import get_visualisation, get_visualisation_spec


class CollectionPageView(RenderedMarkdownView):
    template_name = "collections/collection_page.jinja"

    def get_markdown_file_path(self):
        root_dir = settings.DATAGOVUK_CONTENT_COLLECTIONS_ROOT
        return f"{root_dir}{self.kwargs['collection_name']}/{self.kwargs['collection_page_name']}.md"

    @property
    def collection_pages(self):
        collection_pages = []
        selected_index = 0

        collection = COLLECTIONS_BY_SLUG[self.kwargs["collection_name"]]

        for index, topic in enumerate(collection["topics"]):
            selected_index = index if topic["slug"] == self.kwargs["collection_page_name"] else selected_index
            is_selected: bool = topic["slug"] == self.kwargs["collection_page_name"]
            collection_pages.append(
                {
                    **topic,
                    "url": f"/collections/{self.kwargs['collection_name']}/{topic['slug']}",
                    "selected": is_selected,
                },
            )

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
        if context["visualisation_data"]:
            context["visualisation"] = get_visualisation(context["visualisation_data"])

        return context


class CollectionDownloadView(View):
    def get(self, request, collection_name, collection_page_name):
        markdown_file_path = get_safe_markdown_path(
            f"{settings.DATAGOVUK_CONTENT_COLLECTIONS_ROOT}{collection_name}/{collection_page_name}.md",
        )

        context = get_template_context_from_markdown(markdown_file_path)
        visualisation_data_path = context.get("visualisation_data")
        visualisation_spec = get_visualisation_spec(visualisation_data_path)
        if not visualisation_spec:
            error_message = "No visualisation available"
            raise Http404(error_message)

        download_filename = visualisation_spec.get("download", "missing")
        csv_path = visualisation_spec["data_path"].parent / download_filename
        if not csv_path.exists():
            error_message = "No download available"
            raise Http404(error_message)

        return FileResponse(
            csv_path.open("rb"),
            as_attachment=True,
            filename=download_filename,
            content_type="text/csv",
        )


class CollectionView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        collection_name = self.kwargs["collection_name"]
        try:
            for collection in COLLECTIONS:
                if collection_name == collection["slug"]:
                    if len(collection["topics"]) < 1:
                        message = f"Collection {collection_name} has no topics"
                        raise Http404(message)
                    collection_page_name = collection["topics"][0]["slug"]
                    break
            else:
                message = f"Collection {collection_name} not found"
                raise Http404(message)
        except KeyError as error:
            message = f"Collection {collection_name} malformed"
            raise Http404(message) from error
        return reverse(
            "collections:collection_page",
            kwargs={
                "collection_name": self.kwargs["collection_name"],
                "collection_page_name": collection_page_name,
            },
        )
