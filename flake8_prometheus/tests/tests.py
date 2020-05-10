import ast

import pytest
from prometheus_client import (Counter, Histogram, Gauge, Summary, Info)

from flake8_prometheus.flake8_prometheus import PrometheusChecker

GENERAL_METRICS = [Counter, Histogram, Gauge, Summary, Info]

base_error = PrometheusChecker._error_template.format('"some_"')
BAD_NAME_ERROR = f'{base_error}, got "bad_name" instead'


@pytest.mark.parametrize('statement', [
    'c = {}("some_name", "some description")',
    'c = {}("some_name", documentation="some description")',
    "c = {}(name='some_name', documentation='some doc')",
    "c = {}(documentation='some doc', name='some_name')",
])
@pytest.mark.parametrize('klass', GENERAL_METRICS, indirect=True)
def test_check_name_ok(statement, klass):
    statement = statement.format(klass.__name__)
    assert not list(PrometheusChecker(ast.parse(statement), 'module.py').run())


@pytest.mark.parametrize('statement', [
    'c = {}("bad_name", "some description")',
    'c = {}("bad_name", documentation="some description")',
    "c = {}(name='bad_name', documentation='some doc')",
    "c = {}(documentation='some doc', name='bad_name')",
])
@pytest.mark.parametrize('klass', GENERAL_METRICS, indirect=True)
def test_check_name_fail(statement, klass):
    tree = ast.parse(statement.format(klass.__name__))
    actual_error = list(PrometheusChecker(tree, 'module.py').run())[0][2]
    assert actual_error == BAD_NAME_ERROR


@pytest.mark.parametrize('statement', [
    'c = {}("bad_name")',
    'c = {}(documentation="some description")',
    'c = {}(1, 2)',
    'c = {}(1, "2")',
    'c = {}("1", 2)',
    'c = {}([1, 2], "some")',
    'c = {}(["some_name", "some"], "some")',
    'c = {}(dict(a="b", s=None), "some")',
    'c = {}(set(1, 2, 3), "some")',
    'c = {}(tuple(1, 2, 3), "some")',
])
def test_cannot_instance_metric(statement, klass):
    tree = ast.parse(statement.format(klass.__name__))
    assert not list(PrometheusChecker(tree, 'module.py').run())


def test_full_metric_definition(full_definition):
    tree = ast.parse(full_definition)
    assert not list(PrometheusChecker(tree, 'module.py').run())
