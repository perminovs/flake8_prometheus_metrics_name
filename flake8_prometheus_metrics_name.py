import ast

from prometheus_client.metrics import MetricWrapperBase


class Checker:
    name = 'flake8-prometheus-metrics-name'
    version = '0.1.3'

    _error_template = (
        'PRM902: Metric name should start with one of following prefixes: {}'
    )
    _valid_name_prefixes = ()
    _disabled = False

    def __init__(self, tree, filename):
        # `filename` arg is required to implement flake8 checker interface

        if self._disabled:
            return

        self._tree = tree

        if not self._valid_name_prefixes:
            raise ValueError(
                'No prefixes for metric name provided. '
                'Ensure option "prometheus-metrics-name-prefixes" is set.'
            )
        prefixes = ', '.join(f'"{s}"' for s in self._valid_name_prefixes)
        self._error_msg = self._error_template.format(prefixes)

        self._node_id_to_prometheus = {
            klass.__name__: klass
            for klass in _get_all_subclasses(MetricWrapperBase)
        }

    @classmethod
    def add_options(cls, parser):
        parser.add_option(
            "--prometheus-metrics-name-prefixes",
            default="",
            action="store",
            type="string",
            help="Possible prometheus metric name prefixes",
            parse_from_config=True,
            comma_separated_list=True,
        )
        parser.add_option(
            "--prometheus-metrics-disabled",
            default=False,
            action="store",
            type="int",
            help="Enabling linter",
            parse_from_config=True,
            comma_separated_list=False,
        )

    @classmethod
    def parse_options(cls, options):
        cls._disabled = bool(options.prometheus_metrics_disabled)
        if cls._disabled:
            return

        prefixes = options.prometheus_metrics_name_prefixes
        if not isinstance(prefixes, (list, tuple)):
            prefixes = prefixes.split(',')
        cls._valid_name_prefixes = tuple(p.strip() for p in prefixes)

    def run(self):
        if self._disabled:
            return []

        for statement in ast.walk(self._tree):
            if not isinstance(statement, ast.Call):
                continue

            called = getattr(statement.func, 'id', None)
            if called is None:
                continue
            cls = self._node_id_to_prometheus.get(called)
            if not cls:
                continue

            args = [_parse_argument(arg) for arg in statement.args]
            kwargs = {
                kw.arg: _parse_argument(kw.value)
                for kw in statement.keywords
            }
            try:
                metric = cls(*args, **kwargs)
            except (ValueError, TypeError):
                continue

            for prefix in self._valid_name_prefixes:
                if metric._name.startswith(prefix):
                    break
            else:
                yield (
                    statement.lineno,
                    statement.col_offset,
                    f'{self._error_msg}, got "{metric._name}" instead',
                    type(self),
                )


def _parse_argument(ast_node):
    if isinstance(ast_node, ast.Constant):
        return ast_node.value
    if isinstance(ast_node, ast.Tuple):
        return [_parse_argument(inner_node) for inner_node in ast_node.elts]

    return ast_node


def _get_all_subclasses(klass):
    all_subclasses = []

    for subclass in klass.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(_get_all_subclasses(subclass))

    return all_subclasses
