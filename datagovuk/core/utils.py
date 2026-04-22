import logging

import sentry_sdk

logger = logging.getLogger(__name__)


def capture_exception(exception):
    logger.exception(exception)
    is_sentry_initialised = bool(sentry_sdk.get_client().dsn)
    if is_sentry_initialised:
        sentry_sdk.capture_exception(exception)
