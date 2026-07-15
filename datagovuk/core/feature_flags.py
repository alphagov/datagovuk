from functools import wraps

from django.conf import settings
from django.http import Http404


def is_feature_flag_enabled(feature_flag):
    return feature_flag.value in settings.FEATURE_FLAGS_ENABLED


# Can be removed with flag once all released
def flag_required(flag, view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not is_feature_flag_enabled(flag):
            raise Http404
        return view_func(request, *args, **kwargs)

    return wrapped
