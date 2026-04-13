from datetime import date

from django.views.generic import TemplateView


class CollectionPage(TemplateView):
    template_name = "collections/collection_page.jinja"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        collection = {
            "title": "Inflation",
            "slug": self.kwargs["collection_page_name"],
            "collection": "Business and economy",
            "collection_slug": self.kwargs["collection_name"],
            "websites": [
                {
                    "url": "https://www.ons.gov.uk/economy/inflationandpriceindices",
                    "link_text": "Inflation and price indices",
                },
            ],
            "api": {
                "url": "https://www.ons.gov.uk/economy/inflationandpriceindices",
                "link_text": "Inflation and price indices",
            },
            "dataset": {
                "url": "https://www.ons.gov.uk/economy/inflationandpriceindices",
                "link_text": "Inflation and price indices",
            },
            "page_last_updated": date.strptime("2026-03-25", "%Y-%m-%d"),
            "visualisation_data": "inflation/inflation.json",
            "contact": "",
            "status": "for-publication",
            "body": """
            <p class="govuk-body-m datagovuk-body">
                Explore various datasets about inflation and price indices published by the Office for
                National Statistics (ONS).
                You can download the data as a PNG, CSV or XLS file.
            </p>

            <p class="govuk-body-m datagovuk-body">
                Inflation refers to the rate at which the general level of prices for
                goods and services rises, while a price index measures the average change in prices over time.
                Measures of inflation and prices include consumer price inflation, producer price
                inflation and the House Price Index.
            </p>
            """,
        }
        context["collection"] = collection
        return context
