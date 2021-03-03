# 3p
import rediscluster

# project
from ddtrace import config
from ddtrace.vendor import wrapt

from .. import trace_utils
from ...constants import SPAN_MEASURED_KEY
from ...ext import SpanTypes
from ...ext import redis as redisx
from ...pin import Pin
from ...utils.wrappers import unwrap
from ..redis.patch import traced_execute_command
from ..redis.patch import traced_pipeline
from ..redis.util import format_command_args


# DEV: In `2.0.0` `__version__` is a string and `VERSION` is a tuple,
#      but in `1.x.x` `__version__` is a tuple annd `VERSION` does not exist
REDISCLUSTER_VERSION = getattr(rediscluster, 'VERSION', rediscluster.__version__)


def patch():
    """Patch the instrumented methods
    """
    if getattr(rediscluster, '_datadog_patch', False):
        return
    setattr(rediscluster, '_datadog_patch', True)

    _w = wrapt.wrap_function_wrapper
    if REDISCLUSTER_VERSION >= (2, 0, 0):
        _w('rediscluster', 'client.RedisCluster.execute_command', traced_execute_command)
        _w('rediscluster', 'client.RedisCluster.pipeline', traced_pipeline)
        _w('rediscluster', 'pipeline.ClusterPipeline.execute', traced_execute_pipeline)
        Pin(service=redisx.DEFAULT_SERVICE, app=redisx.APP).onto(rediscluster.RedisCluster)
    else:
        _w('rediscluster', 'StrictRedisCluster.execute_command', traced_execute_command)
        _w('rediscluster', 'StrictRedisCluster.pipeline', traced_pipeline)
        _w('rediscluster', 'StrictClusterPipeline.execute', traced_execute_pipeline)
        Pin(service=redisx.DEFAULT_SERVICE, app=redisx.APP).onto(rediscluster.StrictRedisCluster)


def unpatch():
    if getattr(rediscluster, '_datadog_patch', False):
        setattr(rediscluster, '_datadog_patch', False)

        if REDISCLUSTER_VERSION >= (2, 0, 0):
            unwrap(rediscluster.client.RedisCluster, 'execute_command')
            unwrap(rediscluster.client.RedisCluster, 'pipeline')
            unwrap(rediscluster.pipeline.ClusterPipeline, 'execute')
        else:
            unwrap(rediscluster.StrictRedisCluster, 'execute_command')
            unwrap(rediscluster.StrictRedisCluster, 'pipeline')
            unwrap(rediscluster.StrictClusterPipeline, 'execute')


#
# tracing functions
#

def traced_execute_pipeline(func, instance, args, kwargs):
    pin = Pin.get_from(instance)
    if not pin or not pin.enabled():
        return func(*args, **kwargs)

    cmds = [format_command_args(c.args) for c in instance.command_stack]
    resource = '\n'.join(cmds)
    tracer = pin.tracer
    with tracer.trace(redisx.CMD, resource=resource, service=pin.service, span_type=SpanTypes.REDIS) as s:
        s.set_tag(SPAN_MEASURED_KEY)
        s.set_tag(redisx.RAWCMD, resource)
        s.set_metric(redisx.PIPELINE_LEN, len(instance.command_stack))

        trace_utils.set_analytics_sample_rate(s, config.rediscluster)

        return func(*args, **kwargs)
