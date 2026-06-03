import pytest


@pytest.fixture
def enable_feature_flag(settings):
    def _set_feature_flag(feature_flag):
        settings.FEATURE_FLAGS_ENABLED.append(feature_flag)

    return _set_feature_flag


@pytest.fixture
def disable_feature_flag(settings):
    def _unset_feature_flag(feature_flag):
        settings.FEATURE_FLAGS_ENABLED.remove(feature_flag)

    return _unset_feature_flag


@pytest.fixture
def enable_early_years(enable_feature_flag, disable_feature_flag):
    enable_feature_flag("early-years")
    yield
    disable_feature_flag("early-years")
