from functools import wraps

from django.conf import settings
from django.http import Http404
from django.urls import path

from datagovuk.core.feature_flags import is_feature_flag_enabled

from . import views

app_name = "directory"


# Can be removed with flag once all releases
def _flag_required(flag, view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not is_feature_flag_enabled(flag):
            raise Http404
        return view_func(request, *args, **kwargs)

    return wrapped


urlpatterns = [
    path(
        "search",
        _flag_required(settings.FEATURE_FLAGS.SOLR_SEARCH, views.SearchView.as_view()),
        name="search",
    ),
    path(
        "dataset/<uuid:uuid>/<slug:slug>",
        _flag_required(settings.FEATURE_FLAGS.SOLR_SEARCH, views.DatasetView.as_view()),
        name="dataset",
    ),
]
