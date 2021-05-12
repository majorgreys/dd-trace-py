import logging

from . import constants


class DDLogFormatter(logging.Formatter):
    def format(self, record):
        for attr in [
            constants.RECORD_ATTR_TRACE_ID,
            constants.RECORD_ATTR_SPAN_ID,
        ]:
            if not hasattr(record, attr):
                setattr(record, attr, constants.RECORD_ATTR_VALUE_ZERO)
        for attr in [
            constants.RECORD_ATTR_ENV,
            constants.RECORD_ATTR_VERSION,
            constants.RECORD_ATTR_SERVICE,
        ]:
            if not hasattr(record, attr):
                setattr(record, attr, constants.RECORD_ATTR_VALUE_EMPTY)
        return super(DDLogFormatter, self).format(record)
