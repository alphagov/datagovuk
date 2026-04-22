import logging
from unittest.mock import MagicMock

from datagovuk.core.utils import capture_exception


def test_capture_exception_no_sentry(caplog):
    with caplog.at_level(logging.DEBUG):
        capture_exception(NotImplementedError("My exception"))
    log_record = caplog.records[-1]
    assert log_record.message == "My exception"


def test_capture_exception_with_sentry(caplog, monkeypatch):
    class MockedClient:
        dsn = True

    monkeypatch.setattr(
        "datagovuk.core.utils.sentry_sdk.get_client",
        lambda: MockedClient,
    )
    mocked_capture_exception = MagicMock()
    monkeypatch.setattr(
        "datagovuk.core.utils.sentry_sdk.capture_exception",
        mocked_capture_exception,
    )
    exception = NotImplementedError("My exception")
    capture_exception(exception)
    mocked_capture_exception.assert_called_once()
    mocked_capture_exception.assert_called_with(exception)
