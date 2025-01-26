PHONY: install format lint test docs clean

install:
	pip install -e ".[dev,docs]"

format:
	black src tests
	isort src tests

lint:
	ruff src tests
	mypy src tests

test:
	pytest tests/ -v --cov=my_ppi_package

docs:
	cd docs && make html

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info