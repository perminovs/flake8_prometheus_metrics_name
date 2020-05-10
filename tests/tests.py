import ast

import pytest
from prometheus_client import Counter, Gauge, Histogram, Info, Summary

from flake8_prometheus_metrics_name.api import Api

GENERAL_METRICS = [Counter, Histogram, Gauge, Summary, Info]

VALID_PREFIX = 'some_'
base_error = Api._error_template.format(f'"{VALID_PREFIX}"')
BAD_NAME_ERROR = f'{base_error}, got "bad_name" instead'


@pytest.fixture(autouse=True)
def _set_valid_prefix():
    Api._valid_name_prefixes = (VALID_PREFIX,)


@pytest.mark.parametrize(
    'statement',
    [
        'c = {}("some_name", "some description")',
        'c = {}("some_name", documentation="some description")',
        "c = {}(name='some_name', documentation='some doc')",
        "c = {}(documentation='some doc', name='some_name')",
    ],
)
@pytest.mark.parametrize('klass', GENERAL_METRICS, indirect=True)
def test_check_name_ok(statement, klass):
    statement = statement.format(klass.__name__)
    assert not list(Api(ast.parse(statement), 'module.py').run())


@pytest.mark.parametrize(
    'statement',
    [
        'c = {}{}("bad_name", "some description")',
        'c = {}{}("bad_name", documentation="some description")',
        "c = {}{}(name='bad_name', documentation='some doc')",
        "c = {}{}(documentation='some doc', name='bad_name')",
    ],
)
@pytest.mark.parametrize('call_prefix', ['', 'pc.'])
@pytest.mark.parametrize('klass', GENERAL_METRICS, indirect=True)
def test_check_name_fail(statement, klass, call_prefix):
    tree = ast.parse(statement.format(call_prefix, klass.__name__))
    actual_error = list(Api(tree, 'module.py').run())[0][2]
    assert actual_error == BAD_NAME_ERROR


@pytest.mark.parametrize(
    'statement',
    [
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
    ],
)
def test_cannot_instance_metric(statement, klass):
    tree = ast.parse(statement.format(klass.__name__))
    assert not list(Api(tree, 'module.py').run())


def test_full_metric_definition(full_definition):
    tree = ast.parse(full_definition)
    assert not list(Api(tree, 'module.py').run())


def test_no_prefix_provided():
    expected_error = (
        'No prefixes for metric name provided. '
        'Ensure option "prometheus-metrics-name-prefixes" is set.'
    )
    Api._valid_name_prefixes = ()
    with pytest.raises(ValueError, match=expected_error):
        Api(ast.AST(), 'None')


def test_calling_object_attribute():
    code = 'a = A()\n' "a.method('data', arg=4)"
    tree = ast.parse(code)
    assert not list(Api(tree, 'module.py').run())


@pytest.mark.parametrize(
    'statement', ['c = {}("bad_name", "some description")']
)
@pytest.mark.parametrize('klass', [Counter], indirect=True)
def test_disabling(statement, klass):
    Api._disabled = True
    tree = ast.parse(statement.format(klass.__name__))
    assert not list(Api(tree, 'module.py').run())
