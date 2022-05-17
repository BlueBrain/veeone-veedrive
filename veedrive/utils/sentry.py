import logging

import sentry_sdk
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from .. import config


def set_up():
    sentry_logging = LoggingIntegration(
        level=logging.DEBUG,  # Capture debug and above as breadcrumbs
        event_level=logging.WARNING,  # Send errors as events
    )

    sentry_sdk.init(
        dsn=config.SENTRY_DSN,
        integrations=[sentry_logging, AioHttpIntegration()],
        environment=config.ENVIRONMENT,
        traces_sample_rate=config.SENTRY_SAMPLE_RATE,
        debug=config.SENTRY_DEBUG,
        http_proxy=config.HTTP_PROXY,
    )
