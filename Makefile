test: install
	pytest tests

cov: install
	pytest --cov=regex tests/

install:
	python setup.py develop

flake8: install
	flake8 regex

.PHONY: test cov install flake8
