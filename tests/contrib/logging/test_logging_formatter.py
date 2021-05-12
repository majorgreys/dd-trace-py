import logging

import pytest
import six

from ddtrace.contrib.logging import patch
from ddtrace.contrib.logging import unpatch
from ddtrace.contrib.logging.utils import DDLogFormatter


DEFAULT_FORMAT = "%(message)s"
DD_LOG_FORMAT = (
    "%(message)s - dd.service=%(dd.service)s dd.version=%(dd.version)s dd.env=%(dd.env)s"
    " dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s"
)


@pytest.mark.parametrize(
    "patched, format, formatter_cls, captured_predicate",
    [
        (False, DEFAULT_FORMAT, logging.Formatter, lambda c: c.err == ""),
        (True, DEFAULT_FORMAT, logging.Formatter, lambda c: c.err == ""),
        (
            False,
            DD_LOG_FORMAT,
            logging.Formatter,
            lambda c: c.err.startswith("--- Logging error ---") and "KeyError: 'dd.service'" in c.err,
        ),
        (True, DD_LOG_FORMAT, logging.Formatter, lambda c: c.err == ""),
        # this fails when run with all others but not on its own
        (False, DEFAULT_FORMAT, DDLogFormatter, lambda c: c.err == ""),
        (True, DEFAULT_FORMAT, DDLogFormatter, lambda c: c.err == ""),
        # this fails when run with all others but not on its own
        (False, DD_LOG_FORMAT, DDLogFormatter, lambda c: c.err == ""),
        (True, DD_LOG_FORMAT, DDLogFormatter, lambda c: c.err == ""),
    ],
)
def test_log_formatter(capsys, patched, format, formatter_cls, captured_predicate):
    try:
        if patched:
            patch()
        logger = logging.getLogger("test_log_formatter")
        logger.setLevel(logging.INFO)
        stream = six.StringIO()
        ch = logging.StreamHandler(stream)
        formatter = formatter_cls(format)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.info("info message")
        captured = capsys.readouterr()
        assert captured_predicate(captured)
    finally:
        unpatch()
