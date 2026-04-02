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
