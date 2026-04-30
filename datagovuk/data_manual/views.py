from copy import deepcopy

from django.conf import settings

from datagovuk.core.views import RenderedMarkdownView

from .constants import DATA_MANUAL_PAGES, DATA_MANUAL_PAGES_BY_SLUG


class DataManualView(RenderedMarkdownView):
    template_name = "data_manual/content.jinja"

    def get_markdown_file_path(self):
        return f"{settings.DATAGOVUK_CONTENT_DATA_MANUAL_ROOT}{self.kwargs['data_manual_name']}.md"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = DATA_MANUAL_PAGES_BY_SLUG[self.kwargs["data_manual_name"]]["title"]
        context["side_nav_items"] = self.side_nav_items

        return context

    @property
    def side_nav_items(self):
        data_manual_items = []
        for item in deepcopy(DATA_MANUAL_PAGES):
            if item["slug"] == self.kwargs["data_manual_name"]:
                item["selected"] = True

            data_manual_items.append(item)

        return data_manual_items
