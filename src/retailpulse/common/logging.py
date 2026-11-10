"""Structured logging setup."""

import logging


def configure_logging() -> None:
    """Configure one consistent application log format."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s correlation_id=%(correlation_id)s %(message)s",
    )


class CorrelationAdapter(logging.LoggerAdapter):
    """Attach a correlation identifier to structured log records."""

    def process(self, msg, kwargs):
        extra = kwargs.setdefault("extra", {})
        extra.setdefault("correlation_id", self.extra.get("correlation_id", "-"))
        return msg, kwargs
