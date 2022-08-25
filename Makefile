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
	HOST_VEEDRIVE_MEDIA_PATH=`pwd`/tests/sandbox_folder \
		docker compose -f docker-compose.yml  -f docker-compose-dev.yml run  --service-ports --rm backend -m pytest --cov=veedrive -s -v
	docker compose down

run-docker-dev:
	HOST_VEEDRIVE_MEDIA_PATH=`pwd`/tests/sandbox_folder docker compose  -f docker-compose.yml -f docker-compose-dev.yml up

install-dev:
	pip install -e .

clean-pyc:
	find -name '*.pyc' -exec rm --force {} +
	find -name '*.pyo' -exec rm --force {} +

docs:
	cd docs; sphinx-apidoc  -o . .. ; make html

coverage:
	python -m pytest --cov=veedrive

