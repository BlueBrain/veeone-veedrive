isort:
	sh -c "isort --skip-glob=.tox --recursive . "

black:
	sh -c "black . "

precommit:
	make black; make isort

venv:
	virtualenv -p `which python3` venv

install-dev:
	pip install -e .

functional-tests:
	$(foreach file, $(wildcard tests/*e2e*), python $(file) || exit ;)

clean-pyc:
	find -name '*.pyc' -exec rm --force {} +
	find -name '*.pyo' -exec rm --force {} +

docs:
	cd docs; sphinx-apidoc  -o . .. ; make html
