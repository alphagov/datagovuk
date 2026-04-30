from datetime import date

from django.conf import settings
from django.http import FileResponse, Http404
from django.urls import reverse
from django.views.generic.base import RedirectView, View

from datagovuk.core.markdown import get_safe_markdown_path, get_template_context_from_markdown
from datagovuk.core.views import RenderedMarkdownView

from .constants import COLLECTIONS
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
            collection_page_name = COLLECTIONS[collection_name][0]["slug"]
        except KeyError as error:
            message = f"Collection {collection_name} not found"
            raise Http404(message) from error
        return reverse(
            "collections:collection_page",
            kwargs={
                "collection_name": self.kwargs["collection_name"],
                "collection_page_name": collection_page_name,
            },
        )
