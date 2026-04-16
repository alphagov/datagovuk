DATA_MANUAL_PAGES = [
    {
        "title": "Who this manual is for",
        "slug": "who-this-manual-is-for",
        "url": "/data-manual/who-this-manual-is-for",
        "description": "Find out if this manual can help you and why it's important",
        "icon": "user",
    },
    {
        "title": "Data management",
        "slug": "data-management",
        "url": "/data-manual/data-management",
        "description": "Understand data roles and responsibilities, and how to manage data quality",
        "icon": "database",
    },
    {
        "title": "Data standards",
        "slug": "data-standards",
        "url": "/data-manual/data-standards",
        "description": "A range of standards for improving how data is used across government",
        "icon": "document",
    },
    {
        "title": "Security",
        "slug": "security",
        "url": "/data-manual/security",
        "description": "Strategies, policies and guidance to make your service safer",
        "icon": "padlock",
    },
    {
        "title": "Data protection and privacy",
        "slug": "data-protection-and-privacy",
        "url": "/data-manual/data-protection-and-privacy",
        "description": "How to comply with the Data Protection Act 2018 and UK GDPR",
        "icon": "shield",
    },
    {
        "title": "Data sharing",
        "slug": "data-sharing",
        "url": "/data-manual/data-sharing",
        "description": "Frameworks and guides about sharing data between government organisations",
        "icon": "sharing",
    },
    {
        "title": "AI and data-driven technologies",
        "slug": "ai-and-data-driven-technologies",
        "url": "/data-manual/ai-and-data-driven-technologies",
        "description": "How to use AI safely and effectively in government",
        "icon": "stars",
    },
    {
        "title": "APIs and technical guidance",
        "slug": "apis-and-technical-guidance",
        "url": "/data-manual/apis-and-technical-guidance",
        "description": "How to build APIs in government and improve API standards",
        "icon": "api",
    },
    {
        "title": "General guidance",
        "slug": "general-guidance",
        "url": "/data-manual/general-guidance",
        "description": "Where to start when you're creating a new public service",
        "icon": "open-book",
    },
]

DATA_MANUAL_OTHER_PAGES = [
    {
        "title": "Tell us what you think",
        "slug": "tell-us-what-you-think",
    },
    {
        "title": "Join a data community",
        "slug": "join-a-data-community",
    },
]

DATA_MANUAL_PAGES_BY_SLUG = {item["slug"]: item for item in DATA_MANUAL_PAGES + DATA_MANUAL_OTHER_PAGES}
