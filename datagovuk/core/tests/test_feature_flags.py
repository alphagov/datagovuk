from datagovuk.core.feature_flags import is_feature_flag_enabled


def test_is_feature_flag_enabled_flag_enabled(settings):
    settings.FEATURE_FLAGS_ENABLED = ["test-feature-flag"]
    assert is_feature_flag_enabled(settings.FEATURE_FLAGS.TEST_FEATURE_FLAG) is True


def test_is_feature_flag_enabled_flag_disabled(settings):
    settings.FEATURE_FLAGS_ENABLED = []
    assert is_feature_flag_enabled(settings.FEATURE_FLAGS.TEST_FEATURE_FLAG) is False
