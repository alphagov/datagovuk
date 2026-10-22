from django.urls import reverse

HELP_PAGES = [
    {
        "title": "About the National Data Library",
        "url": reverse("pages:about"),
        "description": "What the National Data Library is, how it works and plans for the future",
    },
    {
        "title": "Data manual",
        "url": reverse("data_manual:home"),
        "description": "Guidance and standards for people who work with data in the public sector.",
    },
    {
        "title": "Help for publishers",
        "url": "https://guidance.data.gov.uk/publish_and_manage_data/",
        "description": "How too add, update and maintain datasets in the directory.",
    },
    {
        "title": "API documentation",
        "url": reverse("data_manual:data_manual_page", kwargs={"data_manual_name": "apis-and-technical-guidance"}),
        "description": "Technical guidance for using the National Data Library directory API.",
    },
    {
        "title": "Curated collections",
        "url": reverse("pages:data_curation"),
        "description": "How we select data for collections and how to suggest additions.",
    },
    {
        "title": "Support",
        "url": reverse("support:support-form"),
        "description": "Get support, report a problem and provide feedback.",
    },
]
