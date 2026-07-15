from django.conf import settings
from django.urls import path

from datagovuk.core.feature_flags import flag_required

from . import views

app_name = "directory"

urlpatterns = [
    path(
        "search/",
        _flag_required(settings.FEATURE_FLAGS.SOLR_SEARCH, views.SearchView.as_view()),
        name="search",
    ),
    path(
        "dataset/<uuid:uuid>/<slug:slug>",
        flag_required(settings.FEATURE_FLAGS.SOLR_SEARCH, views.DatasetView.as_view()),
        name="dataset",
    ),
]
