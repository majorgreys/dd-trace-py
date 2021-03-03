from copy import deepcopy
import os

from .._hooks import Hooks
from ..utils.attrdict import AttrDict
from ..utils.formats import asbool
from ..utils.formats import get_env
from .http import HttpConfig


class IntegrationConfig(AttrDict):
    """
    Integration specific configuration object.

    This is what you will get when you do::

        from ddtrace import config

        # This is an `IntegrationConfig`
        config.flask

        # `IntegrationConfig` supports both attribute and item accessors
        config.flask['service_name'] = 'my-service-name'
        config.flask.service_name = 'my-service-name'
    """

    def __init__(self, global_config, name, *args, **kwargs):
        """
        :param global_config:
        :type global_config: Config
        :param args:
        :param kwargs:
        """
        super(IntegrationConfig, self).__init__(*args, **kwargs)

        # Set internal properties for this `IntegrationConfig`
        # DEV: By-pass the `__setattr__` overrides from `AttrDict` to set real properties
        object.__setattr__(self, "global_config", global_config)
        object.__setattr__(self, "integration_name", name)
        object.__setattr__(self, "hooks", Hooks())
        object.__setattr__(self, "http", HttpConfig())

        # Set default analytics configuration, default is disabled
        # DEV: Default to `None` which means do not set this key
        # Inject environment variables for integration
        old_analytics_enabled = get_env(name, "analytics_enabled")
        analytics_enabled = os.environ.get("DD_TRACE_%s_ANALYTICS_ENABLED" % name.upper(), old_analytics_enabled)
        if analytics_enabled is not None:
            analytics_enabled = asbool(analytics_enabled)

        old_analytics_rate = get_env(name, "analytics_sample_rate", default=1.0)
        analytics_rate = float(os.environ.get("DD_TRACE_%s_ANALYTICS_SAMPLE_RATE" % name.upper(), old_analytics_rate))

        self.setdefault("analytics_enabled", analytics_enabled)
        self.setdefault("analytics_sample_rate", analytics_rate)

        service = get_env(name, "service", default=get_env(name, "service_name", default=None))
        self.setdefault("service", service)
        # TODO[v1.0]: this is required for backwards compatibility since some
        # integrations use service_name instead of service. These should be
        # unified.
        self.setdefault("service_name", service)

    def __deepcopy__(self, memodict=None):
        new = IntegrationConfig(self.global_config, self.integration_name, deepcopy(dict(self), memodict))
        new.hooks = deepcopy(self.hooks, memodict)
        new.http = deepcopy(self.http, memodict)
        return new

    def copy(self):
        new = IntegrationConfig(self.global_config, self.integration_name, dict(self))
        new.hooks = self.hooks
        new.http = self.http
        return new

    @property
    def trace_query_string(self):
        if self.http.trace_query_string is not None:
            return self.http.trace_query_string
        return self.global_config.http.trace_query_string

    def header_is_traced(self, header_name):
        """
        Returns whether or not the current header should be traced.
        :param header_name: the header name
        :type header_name: str
        :rtype: bool
        """
        return (
            self.http.header_is_traced(header_name)
            if self.http.is_header_tracing_configured
            else self.global_config.header_is_traced(header_name)
        )

    def _is_analytics_enabled(self):
        use_global_config = getattr(self, "_use_global_config_analytics", False)
        # DEV: analytics flag can be None which should not be taken as
        # enabled when global flag is disabled
        if use_global_config and self.global_config.analytics_enabled:
            return self.analytics_enabled is not False
        else:
            return self.analytics_enabled is True

    def __repr__(self):
        cls = self.__class__
        keys = ", ".join(self.keys())
        return "{}.{}({})".format(cls.__module__, cls.__name__, keys)
