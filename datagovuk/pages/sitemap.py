from django.urls import reverse_lazy

# Pages with a fixed URL. Collections, data manual pages and updates are listed separately.
STATIC_PAGES = [
    {"title": title, "url": reverse_lazy(url_name)}
    for url_name, title in [
        ("pages:home", "Home"),
        ("pages:about", "About"),
        ("pages:roadmap", "Roadmap"),
        ("pages:data_curation", "How we curate data"),
        ("pages:team", "Team"),
        ("pages:publishers", "Publish your data"),
        ("pages:help", "Help"),
        ("pages:accessibility", "Accessibility"),
        ("pages:cookies", "Cookies"),
        ("pages:privacy-and-terms", "Privacy and terms"),
        ("support:support-form", "Support"),
        ("directory:search", "Directory"),
    ]
]
