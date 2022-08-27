isort:
	sh -c "isort --skip-glob=.tox --recursive . "

black:
	sh -c "black . "

precommit:
	make black; make isort

venv:
	virtualenv -p `which python3` venv

run-docker-tests:
	docker compose build
	docker compose run  --service-ports --rm backend -m pytest --cov=veedrive -s -v tests/test_content.py::test_get_image
	docker compose down

prep-hostname:
	cd deploy; ./update_hostname.sh

openstack-up:
	make prep-hostname
	docker-compose up -d

openstack-down:
	docker-compose down

install-dev:
	pip install -e .

clean-pyc:
	find -name '*.pyc' -exec rm --force {} +
	find -name '*.pyo' -exec rm --force {} +

docs:
	cd docs; sphinx-apidoc  -o . .. ; make html

coverage:
	python -m pytest --cov=veedrive

