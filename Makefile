isort:
	sh -c "isort --skip-glob=.tox --recursive . "

black:
	sh -c "black . "

precommit:
	make black; make isort

venv:
	virtualenv -p `which python3` venv

run-docker-tests:
	docker-compose build
	docker-compose run --rm web -m pytest --cov=veedrive -s -v
	docker-compose stop

run-docker:
	docker-compose build
	docker-compose up

install-dev:
	pip install -e .

clean-pyc:
	find -name '*.pyc' -exec rm --force {} +
	find -name '*.pyo' -exec rm --force {} +

docs:
	cd docs; sphinx-apidoc  -o . .. ; make html

coverage:
	python -m pytest --cov=veedrive

