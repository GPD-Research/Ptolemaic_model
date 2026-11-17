.PHONY: install test lint format precommit viewer

install:
	python -m pip install -e '.[dev]'

test:
	python -m pytest -q

lint:
	ruff check .

format:
	ruff format .

precommit:
	pre-commit install
	pre-commit run --all-files

viewer:
	python -m webbrowser viewer/index.html
