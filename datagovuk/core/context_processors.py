from datagovuk.data_manual.constants import DATA_MANUAL_PAGES


def collections(request):
    return {
        "collections": [
            {
                "title": "Business and economy",
                "slug": "business-and-economy",
                "description": "Company information, prices, trade, economic indicators",
            },
            {
                "title": "Environment",
                "slug": "environment",
                "description": "Nature, climate, floods, mapping",
            },
            {
                "title": "Government",
                "slug": "government",
                "description": "Election results, local government finance, Council Tax",
            },
            {
                "title": "Land and property",
                "slug": "land-and-property",
                "description": "Housing, ownership, planning, addresses",
            },
            {
                "title": "People",
                "slug": "people",
                "description": "Population, health, immigration, social mobility",
            },
            {
                "title": "Transport",
                "slug": "transport",
                "description": "Roads, driving, public transport, shipping",
            },
        ],
    }


def data_manual(request):
    return {"data_manual_items": DATA_MANUAL_PAGES}


def data_manual_menu_items(request):
    return {
        "data_manual_menu_items": [
            *DATA_MANUAL_PAGES,
            {
                "title": "Tell us what you think",
                "url": "https://forms.office.com/e/9V26PNFQaR",
                "description": (
                    "We'd love your feedback. Is this manual useful? Can we improve it? Complete a feedback form."
                ),
            },
            {
                "title": "Join a data community",
                "url": "/data-manual/join-a-data-community",
                "description": (
                    "Find Slack channels, events and other ways to connect with data practitioners. Learn more."
                ),
            },
        ],
    }
