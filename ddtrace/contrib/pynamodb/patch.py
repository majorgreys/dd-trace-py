"""
Trace queries to botocore api done via a pynamodb client
"""

import pynamodb.connection.base

from ddtrace import config
from ddtrace.vendor import wrapt

from .. import trace_utils
from ...constants import SPAN_MEASURED_KEY
from ...ext import SpanTypes
from ...pin import Pin
from ...utils.formats import deep_getattr
from ...utils.wrappers import unwrap


# Pynamodb connection class
_PynamoDB_client = pynamodb.connection.base.Connection

config._add(
    "pynamodb",
    {
        "_default_service": "pynamodb",
        "_use_global_config_analytics": True,
    },
)


def patch():
    if getattr(pynamodb.connection.base, "_datadog_patch", False):
        return
    setattr(pynamodb.connection.base, "_datadog_patch", True)

    wrapt.wrap_function_wrapper("pynamodb.connection.base", "Connection._make_api_call", patched_api_call)
    Pin(service=None).onto(pynamodb.connection.base.Connection)


def unpatch():
    if getattr(pynamodb.connection.base, "_datadog_patch", False):
        setattr(pynamodb.connection.base, "_datadog_patch", False)
        unwrap(pynamodb.connection.base.Connection, "_make_api_call")


def patched_api_call(original_func, instance, args, kwargs):

    pin = Pin.get_from(instance)
    if not pin or not pin.enabled():
        return original_func(*args, **kwargs)

    with pin.tracer.trace(
        "pynamodb.command", service=trace_utils.ext_service(pin, config.pynamodb, "pynamodb"), span_type=SpanTypes.HTTP
    ) as span:

        span.set_tag(SPAN_MEASURED_KEY)

        if args and args[0]:
            operation = args[0]
            span.resource = operation

            if args[1] and "TableName" in args[1]:
                table_name = args[1]["TableName"]
                span.set_tag("table_name", table_name)
                span.resource = span.resource + " " + table_name

        else:
            span.resource = "Unknown"
            operation = None

        region_name = deep_getattr(instance, "client.meta.region_name")

        meta = {
            "aws.agent": "pynamodb",
            "aws.operation": operation,
            "aws.region": region_name,
        }
        span.set_tags(meta)

        trace_utils.set_analytics_sample_rate(span, config.pynamodb)

        result = original_func(*args, **kwargs)

        return result
