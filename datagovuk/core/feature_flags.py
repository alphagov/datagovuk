from django.conf import settings


def is_feature_flag_enabled(feature_flag):
    return feature_flag.value in settings.FEATURE_FLAGS_ENABLED
