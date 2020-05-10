import ast
from typing import Dict, Type, Sequence


class MetricNameValidatioError(Exception):
    def __init__(self, name: str):
        self.name = name


def validate_statement(
    statement: ast.AST,
    valid_name_prefixes: Sequence[str],
    prometheus_mapping: Dict[str, Type],
) -> None:
    if not isinstance(statement, ast.Call):
        return

    called = getattr(
        statement.func, 'id',
        getattr(statement.func, 'attr', None),
    )
    if called is None or called not in prometheus_mapping:
        return
    cls = prometheus_mapping[called]

    args = [_parse_call_arguments(arg) for arg in statement.args]
    kwargs = {
        kw.arg: _parse_call_arguments(kw.value)
        for kw in statement.keywords
    }
    try:
        metric = cls(*args, **kwargs)
    except (ValueError, TypeError):
        return

    for prefix in valid_name_prefixes:
        if metric._name.startswith(prefix):
            break
    else:
        raise MetricNameValidatioError(name=metric._name)


def _parse_call_arguments(ast_node):
    if isinstance(ast_node, ast.Constant):
        return ast_node.value
    if isinstance(ast_node, ast.Tuple):
        return [
            _parse_call_arguments(inner_node) for inner_node in ast_node.elts
        ]

    return ast_node
