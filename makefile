.PHONY: test test-silence lint pretty

BIN = .venv/bin/
CODE = flake8_prometheus_metrics_name
TEST = tests

test:
	PYTHONPATH=$(CODE) $(BIN)pytest --verbosity=2 --showlocals --strict --cov=$(CODE) $(TEST)/tests.py

test-silence:
	PYTHONPATH=$(CODE) $(BIN)pytest --cov=$(CODE) $(TEST)/tests.py

lint:
	$(BIN)flake8 --jobs 4 --statistics --show-source $(CODE) $(TEST)
	$(BIN)pylint --jobs 4 --rcfile=setup.cfg $(CODE)
	$(BIN)mypy $(CODE) $(TEST)
	$(BIN)black --target-version py36 --skip-string-normalization --line-length=79 --check $(CODE) $(TEST)

pretty:
	$(BIN)isort --apply --recursive $(CODE) $(TEST)
	$(BIN)black --target-version py36 --skip-string-normalization --line-length=79 $(CODE) $(TEST)
	$(BIN)unify --in-place --recursive $(CODE) $(TEST)
