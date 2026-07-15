from django.conf import settings
from django.urls import path

from datagovuk.core.feature_flags import flag_required

from .views import preview_view

app_name = "preview"

urlpatterns = [
    path(
        "dataset/<uuid:dataset_uuid>/<slug:name>/datafile/<uuid:datafile_uuid>/preview/",
        flag_required(settings.FEATURE_FLAGS.SOLR_SEARCH, preview_view.PreviewView.as_view()),
        name="preview",
    ),
]
