def collections_context(request):
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


DATA_MANUAL_PAGES = [
    {
        "title": "Who this manual is for",
        "url": "/data-manual/who-this-manual-is-for",
        "description": "Find out if this manual can help you and why it's important",
        "icon": "user",
    },
    {
        "title": "Data management",
        "url": "/data-manual/data-management",
        "description": "Understand data roles and responsibilities, and how to manage data quality",
        "icon": "database",
    },
    {
        "title": "Data standards",
        "url": "/data-manual/data-standards",
        "description": "A range of standards for improving how data is used across government",
        "icon": "document",
    },
    {
        "title": "Security",
        "url": "/data-manual/security",
        "description": "Strategies, policies and guidance to make your service safer",
        "icon": "padlock",
    },
    {
        "title": "Data protection and privacy",
        "url": "/data-manual/data-protection-and-privacy",
        "description": "How to comply with the Data Protection Act 2018 and UK GDPR",
        "icon": "shield",
    },
    {
        "title": "Data sharing",
        "url": "/data-manual/data-sharing",
        "description": "Frameworks and guides about sharing data between government organisations",
        "icon": "sharing",
    },
    {
        "title": "AI and data-driven technologies",
        "url": "/data-manual/ai-and-data-driven-technologies",
        "description": "How to use AI safely and effectively in government",
        "icon": "stars",
    },
    {
        "title": "APIs and technical guidance",
        "url": "/data-manual/apis-and-technical-guidance",
        "description": "How to build APIs in government and improve API standards",
        "icon": "api",
    },
    {
        "title": "General guidance",
        "url": "/data-manual/general-guidance",
        "description": "Where to start when you're creating a new public service",
        "icon": "open-book",
    },
]


def data_manual_context(request):
    return {"data_manual_items": DATA_MANUAL_PAGES}


def data_manual_menu_items_context(request):
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
