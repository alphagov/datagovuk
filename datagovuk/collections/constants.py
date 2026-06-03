from django.conf import settings

from datagovuk.core.feature_flags import is_feature_flag_enabled

BASE_COLLECTIONS = [
    {
        "title": "Business and Economy",
        "type": "collection",
        "slug": "business-and-economy",
        "description": "Company information, prices, trade, economic indicators",
        "topics": [
            {"title": "UK trade", "slug": "uk-trade"},
            {"title": "Inflation", "slug": "inflation"},
            {"title": "Bank of England interest rates", "slug": "bank-of-england-interest-rates"},
            {"title": "Get company information", "slug": "get-company-information"},
            {"title": "Get charity information", "slug": "get-charity-information"},
            {"title": "Food hygiene ratings", "slug": "food-hygiene-ratings"},
            {"title": "Fuel and oil prices", "slug": "fuel-and-oil-prices"},
            {"title": "Energy prices", "slug": "energy-prices"},
            {"title": "Electricity", "slug": "electricity"},
            {"title": "Agricultural commodity prices", "slug": "agricultural-commodity-prices"},
        ],
    },
    {
        "title": "Environment",
        "type": "collection",
        "slug": "environment",
        "description": "Nature, climate, floods, mapping",
        "topics": [
            {"title": "Weather", "slug": "weather"},
            {"title": "Air quality", "slug": "air-quality"},
            {"title": "Water quality", "slug": "water-quality"},
            {"title": "Long term flood risk", "slug": "long-term-flood-risk"},
            {"title": "Flood alerts", "slug": "flood-alerts"},
            {"title": "Storm overflows", "slug": "storm-overflows"},
            {"title": "Main rivers", "slug": "main-rivers"},
            {"title": "Coastal erosion", "slug": "coastal-erosion"},
            {"title": "Climate projections", "slug": "climate-projections"},
            {"title": "Environmental public registers", "slug": "public-registers"},
            {"title": "LIDAR mapping", "slug": "lidar"},
            {"title": "Aerial photography mapping", "slug": "aerial-photography"},
            {"title": "Landfill sites", "slug": "landfill-sites"},
            {"title": "Road noise", "slug": "road-noise"},
            {"title": "Rail noise", "slug": "rail-noise"},
            {"title": "Forest and woodlands", "slug": "forest-and-woodlands"},
            {"title": "Non-woodland trees", "slug": "non-woodland-trees"},
            {"title": "Sites of Special Scientific Interest", "slug": "sites-of-special-scientific-interest"},
        ],
    },
    {
        "title": "Government",
        "type": "collection",
        "slug": "government",
        "description": "Election results, local government finance, Council Tax",
        "topics": [
            {"title": "Election results", "slug": "election-results"},
            {"title": "Service assessment reports", "slug": "service-assessment-reports"},
            {"title": "Local government finance", "slug": "local-government-finance"},
            {"title": "Council tax statistics", "slug": "council-tax-statistics"},
            {"title": "Contracts finder", "slug": "contracts-finder"},
            {"title": "Transparency data", "slug": "transparency-data"},
        ],
    },
    {
        "title": "Land and property",
        "type": "collection",
        "slug": "land-and-property",
        "description": "Housing, ownership, planning, addresses",
        "topics": [
            {"title": "UK house prices", "slug": "uk-house-prices"},
            {"title": "Property price paid", "slug": "property-price-paid"},
            {"title": "Land and property ownership", "slug": "land-and-property-ownership"},
            {"title": "Planning data", "slug": "planning-data"},
            {"title": "Addresses", "slug": "addresses"},
            {"title": "Dwelling stock (including vacancies)", "slug": "dwelling-stock"},
            {"title": "Rents, lettings and tenancies", "slug": "rents-lettings-and-tenancies"},
            {"title": "English Housing Survey", "slug": "english-housing-survey"},
            {"title": "Housing supply", "slug": "housing-supply"},
            {"title": "Energy performance of buildings", "slug": "energy-performance-of-buildings"},
            {"title": "Fire statistics", "slug": "fire-statistics"},
        ],
    },
    {
        "title": "People",
        "type": "collection",
        "slug": "people",
        "description": "Population, health, immigration, social mobility",
        "topics": [
            {"title": "Births", "slug": "births"},
            {"title": "Deaths", "slug": "deaths"},
            {"title": "Public health dashboard", "slug": "public-health-dashboard"},
            {"title": "Population estimates", "slug": "population-estimates"},
            {"title": "Immigration", "slug": "immigration"},
            {"title": "Social mobility", "slug": "social-mobility"},
            {"title": "Deprivation", "slug": "deprivation"},
            {"title": "Homelessness", "slug": "homelessness"},
            {"title": "Police recorded crime and outcomes", "slug": "police-recorded-crime-and-outcomes"},
            {"title": "Courts management", "slug": "courts-management"},
            {
                "title": "Early years and childcare inspections and outcomes",
                "slug": "early-years-and-childcare-inspections-and-outcomes",
            },
            {
                "title": "State-funded schools inspections and outcomes",
                "slug": "state-funded-schools-inspections-and-outcomes",
            },
            {"title": "Pupil attendance", "slug": "pupil-attendance"},
            {"title": "Compare school performance", "slug": "compare-school-performance"},
            {"title": "Vocational qualifications", "slug": "vocational-qualifications"},
            {"title": "Museum and gallery visits", "slug": "museum-and-gallery-visits"},
            {"title": "Family food statistics", "slug": "family-food-statistics"},
        ],
    },
    {
        "title": "Transport",
        "type": "collection",
        "slug": "transport",
        "description": "Roads, driving, public transport, shipping",
        "topics": [
            {"title": "Road traffic", "slug": "road-traffic"},
            {"title": "Road safety", "slug": "road-safety"},
            {"title": "Road conditions", "slug": "road-conditions"},
            {"title": "Real-time and historic train information", "slug": "real-time-and-historic-train-information"},
            {"title": "Bus statistics", "slug": "bus-statistics"},
            {"title": "MOT test results", "slug": "mot-results"},
            {"title": "Driving tests", "slug": "driving-tests"},
            {"title": "Fishing vessels", "slug": "fishing-vessels"},
            {"title": "National Travel Survey", "slug": "national-travel-survey"},
            {"title": "Transport connectivity", "slug": "transport-connectivity"},
            {"title": "Maritime and shipping", "slug": "maritime-and-shipping"},
        ],
    },
]


def get_collections():
    # Copy the base list so we don't accidentally mutate the global constant across requests
    collections = list(BASE_COLLECTIONS)

    if is_feature_flag_enabled(settings.FEATURE_FLAGS.EARLY_YEARS):
        collections.append(
            {
                "title": "Early years",
                "type": "spotlight",
                "slug": "early-years",
                "description": "Child development, health, vaccinations, school readiness",
                "topics": [{"title": "Sample page", "slug": "sample-page"}],
            },
        )
    return collections


def get_collections_by_slug():
    return {collection["slug"]: collection for collection in get_collections()}


def get_collections_by_type():
    collections = get_collections()
    return {
        "collection": [collection for collection in collections if collection["type"] == "collection"],
        "spotlight": [collection for collection in collections if collection["type"] == "spotlight"],
    }
