from logging import getLogger

from django.conf import settings

logger = getLogger(__file__)


def is_feature_flag_enabled(feature_flag):
    return feature_flag.value in settings.FEATURE_FLAGS_ENABLED
