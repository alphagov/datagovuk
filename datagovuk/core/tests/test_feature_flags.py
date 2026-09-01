from unittest.mock import Mock

import pytest
from django.http import Http404

from datagovuk.core.feature_flags import flag_required, is_feature_flag_enabled


def test_is_feature_flag_enabled_flag_enabled(settings):
    settings.FEATURE_FLAGS_ENABLED = ["test-feature-flag"]
    assert is_feature_flag_enabled(settings.FEATURE_FLAGS.TEST_FEATURE_FLAG) is True


def test_is_feature_flag_enabled_flag_disabled(settings):
    settings.FEATURE_FLAGS_ENABLED = []
    assert is_feature_flag_enabled(settings.FEATURE_FLAGS.TEST_FEATURE_FLAG) is False


def test_flag_required_calls_view_when_flag_enabled(settings, rf):
    settings.FEATURE_FLAGS_ENABLED = ["test-feature-flag"]

    request = rf.get("/")
    mock_view = Mock(return_value="Success Response")

    decorated_view = flag_required(
        settings.FEATURE_FLAGS.TEST_FEATURE_FLAG,
        mock_view,
    )
    response = decorated_view(request, "arg1", kwarg1="val1")

    mock_view.assert_called_once_with(request, "arg1", kwarg1="val1")
    assert response == "Success Response"


def test_flag_required_raises_404_when_flag_disabled(settings, rf):
    settings.FEATURE_FLAGS_ENABLED = []

    request = rf.get("/")
    mock_view = Mock()

    decorated_view = flag_required(
        settings.FEATURE_FLAGS.TEST_FEATURE_FLAG,
        mock_view,
    )

    with pytest.raises(Http404):
        decorated_view(request)

    mock_view.assert_not_called()
