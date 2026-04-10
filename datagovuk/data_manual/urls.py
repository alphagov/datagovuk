from django.urls import path
from django.views.generic import TemplateView

app_name = "data_manual"

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

urlpatterns = [
    path(
        "",
        TemplateView.as_view(
            template_name="data_manual/home.jinja",
            extra_context={"items": DATA_MANUAL_PAGES},
        ),
        name="home",
    ),
]
