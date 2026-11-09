from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from datagovuk.core.views import RenderedMarkdownView

HELP_PAGES = [
    {
        "title": "About the National Data Library",
        "url": reverse_lazy("pages:about"),
        "description": "What the National Data Library is, how it works and plans for the future.",
    },
    {
        "title": "Data manual",
        "url": reverse_lazy("data_manual:home"),
        "description": "Guidance and standards for people who work with data in the public sector.",
    },
    {
        "title": "Help for publishers",
        "url": "https://guidance.data.gov.uk/publish_and_manage_data/",
        "description": "How to add, update and maintain datasets in the directory.",
    },
    {
        "title": "API documentation",
        "url": "https://guidance.data.gov.uk/get_data/api_documentation/",
        "description": "Technical guidance for using the National Data Library directory API.",
    },
    {
        "title": "Curated collections",
        "url": reverse_lazy("pages:data_curation"),
        "description": "How we select data for collections and how to suggest additions.",
    },
    {
        "title": "Contact",
        "url": reverse_lazy("support:support-form"),
        "description": "Get support, report a problem and provide feedback.",
    },
]


class PagesView(RenderedMarkdownView):
    template_name = "pages/content_page.jinja"

    def get_markdown_file_path(self):
        return f"{settings.DATAGOVUK_CONTENT_PAGES_ROOT}{self.kwargs['slug']}.md"


class HelpView(TemplateView):
    template_name = "pages/help.jinja"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["help_items_1"] = HELP_PAGES[0:3]
        context["help_items_2"] = HELP_PAGES[3:6]

        return context
