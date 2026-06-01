from enum import Enum

from datagovuk.core.context_processors import feature_flags, google_tag_manager


def test_google_tag_manager(settings):
    settings.GOOGLE_TAG_MANAGER_ID = "UA-XXXXX-Y"
    settings.GOOGLE_TAG_MANAGER_AUTH = "fake-auth-token"
    settings.GOOGLE_TAG_MANAGER_PREVIEW = "fake-preview-token"

    context = google_tag_manager(request=None)

    assert context["GOOGLE_TAG_MANAGER_ID"] == "UA-XXXXX-Y"
    assert context["GOOGLE_TAG_MANAGER_AUTH"] == "fake-auth-token"
    assert context["GOOGLE_TAG_MANAGER_PREVIEW"] == "fake-preview-token"


def test_feature_flags(settings):

    class FEATURE_FLAGS(Enum):  # noqa: N801
        TEST_FEATURE_FLAG = "test-feature-flag"

    settings.FEATURE_FLAGS = FEATURE_FLAGS

    context = feature_flags(request=None)

    assert context["FEATURE_FLAGS"] == FEATURE_FLAGS
