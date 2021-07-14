import pytest
from util import gen_traces

from ddtrace.internal.encoding import MsgpackEncoder


@pytest.fixture()
def encoder():
    return MsgpackEncoder()


@pytest.mark.benchmark(group="encoder", warmup=True)
@pytest.mark.parametrize("ntraces", [100])
@pytest.mark.parametrize("nspans", [1000])
def test_encode_trace(benchmark, encoder, ntraces, nspans):
    traces = gen_traces(ntraces=ntraces, nspans=nspans)
    benchmark(encoder.encode_traces, traces)
