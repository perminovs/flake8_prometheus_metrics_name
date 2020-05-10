import pytest
from prometheus_client import (
    REGISTRY,
    Counter,
    Enum,
    Gauge,
    Histogram,
    Info,
    Summary,
)


@pytest.fixture(autouse=True)
def _clear_regestry():
    REGISTRY._names_to_collectors = {}


@pytest.fixture(params=[Counter, Histogram, Gauge, Summary, Info, Enum])
def klass(request):
    return request.param


@pytest.fixture()
def full_definition(klass):
    if klass is Histogram:
        return _histogram_definition()
    if klass is Enum:
        return _enum_definition()
    return _metric_definition(klass)


def _histogram_definition():
    return """from prometheus_client import {klass}

{klass}(
    'some_name',
    'some description',
    labelnames=('label1', 'label2'),
    namespace='some_namespace',
    subsystem='some_subsystem',
    unit='some_unit',
    labelvalues=('label1_val', 'label2_val'),
    buckets=(0.1, 0.5, 1, 5, 10),
)
""".format(
        klass=Histogram.__name__
    )


def _enum_definition():
    return """from prometheus_client import {klass}

{klass}(
    'some_name',
    'some description',
    labelnames=('label1', 'label2'),
    namespace='some_namespace',
    subsystem='some_subsystem',
    unit='some_unit',
    labelvalues=('label1_val', 'label2_val'),
    states=['state1', 'state2'],
)
""".format(
        klass=Enum.__name__
    )


def _metric_definition(klass):
    return """from prometheus_client import {klass}

{klass}(
    'some_name',
    'some description',
    labelnames=('label1', 'label2'),
    namespace='some_namespace',
    subsystem='some_subsystem',
    unit='some_unit',
    labelvalues=('label1_val', 'label2_val'),
    buckets=(0.1, 0.5, 1, 5, 10),
)
""".format(
        klass=klass.__name__
    )
