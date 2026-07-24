from django.conf import settings
from django.urls import path

from datagovuk.core.feature_flags import flag_required

from . import views

app_name = "directory"

urlpatterns = [
    path(
        "search/",
        flag_required(settings.FEATURE_FLAGS.SOLR_SEARCH, views.SearchView.as_view()),
        name="search",
    ),
    path(
        "dataset/<uuid:uuid>/<slug:slug>",
        flag_required(settings.FEATURE_FLAGS.SOLR_SEARCH, views.DatasetView.as_view()),
        name="dataset",
    ),
    path(
        "dataset/<uuid:dataset_uuid>/<slug:name>/datafile/<uuid:datafile_uuid>/preview/",
        flag_required(settings.FEATURE_FLAGS.SOLR_SEARCH, views.PreviewView.as_view()),
        name="preview",
    ),
]
