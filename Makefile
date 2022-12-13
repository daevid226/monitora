ifndef PYTHON_VERSION
override PYTHON_VERSION = 3.8
endif

BRANCH_NAME := $(shell git rev-parse --abbrev-ref HEAD)
PYTHON_CMD := python${PYTHON_VERSION}
POETRY_RUN := poetry run
POETRY_CMD := ${POETRY_RUN} python3
CURDIR := $(PWD)
PG_DATA := $(PWD)/pgdata
PROJECT_NAME := $(notdir ${CURDIR})
DOCKER_TAG_NAME := skip_pay
PROJECT_DIR: ${CURDIR}

export PIP_IGNORE_INSTALLED: 1

ifndef PYTHONPATH
override PYTHONPATH = $(shell ${PYTHON_CMD} -c "import os, sys; print(os.path.dirname(sys.executable))")
endif

## Docker
define DOCKER_BUILD
    @echo "Build docker image with tag name: '${DOCKER_TAG_NAME}'"
    @docker build . -t ${DOCKER_TAG_NAME} --build-arg PYTHON_VERSION=${PYTHON_VERSION} --file 'Dockerfile' --network=host --platform x86_64 $1;
endef

define DOCKER_RUN
    $(call DOCKER_STOP)
    @echo "Run docker with tag name: '${DOCKER_TAG_NAME}'"
    @docker run --env-file .env -a stdout --network=host $1 -ti ${DOCKER_TAG_NAME} $2
endef

define DOCKER_STOP
	@echo "Stop docker image: ${DOCKER_TAG_NAME}"
	@docker stop $$(docker ps -a -q --filter ancestor='${DOCKER_TAG_NAME}') || true
endef

define DOCKER_REMOVE
	$(call DOCKER_STOP)
	@echo "Remove docker images: ${DOCKER_TAG_NAME}"
	@docker rmi $$(docker images | grep '${DOCKER_TAG_NAME}')
endef

define DOCKER_SHOW_IMAGES
	@echo "Run show all docker images by name: ${DOCKER_TAG_NAME}"
	@docker container ls -a | grep "${DOCKER_TAG_NAME}" || true
endef


## Tags
default: help
help:
	@echo "Utils for microservice, check Makefile to choose one"


.PHONY: install install-poetry install-deploy uninstall reinstall reinstall-pre-commit update
install-poetry:
	@echo 'Run install & update poetry and another packages'
	@${PYTHON_CMD} -m pip install --user --upgrade py pip virtualenv poetry wheel setuptools
	@poetry env use ${PYTHON_CMD}
	@poetry config --local
install: install-poetry
	@echo "Run install-dev ${PROJECT_NAME}"
	@${PYTHON_CMD} -m pip install --user --upgrade pre-commit
	@poetry install --no-root --no-interaction
	@pre-commit install
	@pre-commit autoupdate
install-deploy: install-poetry
	@echo "Run test install for deploy"
	@if [ -f "poetry.lock" ]; then \
	  poetry install --only main --no-interaction --no-ansi; \
	else \
	  echo "Missing poetry.lock !"; \
	  exit 1; \
	fi
uninstall:
	@echo "Run uninstall-dev"
	@pre-commit uninstall
	@rm -rf .venv poetry.lock
	@poetry cache clear --all .
reinstall: uninstall install
reinstall-pre-commit:
	@echo "Reinstall pre-commit"
	@pre-commit uninstall
	@pre-commit install
	@pre-commit autoupdate
update:
	@echo "Run update packages"
	@poetry update --dry-run


.PHONY: todo isort pretty lint yamllint pre-commit
todo:
	@grep TODO . -rIn
isort:
	@echo "Run the isort tool and update files that need to"
	@pre-commit run isort --all-files
pretty:
	@echo "Run the black tool and update files that need to"
	@pre-commit run black --all-files
lint:
	@echo "Run mandatory check of code quality"
	@pre-commit run flake8 --all-files
yamllint:
	@echo "Run mandatory check of code quality yaml files"
	@pre-commit run yamllint --all-files
pre-commit:
	@echo "Run pre-commit"
	@pre-commit run --all-files


.PHONY: lock version info check config support list graph freeze shell python
lock:
	@rm -Rf poetry.lock
	@poetry lock
check-lock:
	@if [ ! -f "poetry.lock" ]; then $(MAKE) lock; fi
version:
	@poetry version
info:
	@poetry env list
check:
	@poetry check
config:
	@poetry config --list
list:
	@poetry show
	@list-short
	@poetry show --short
graph:
	@poetry show --tree
freeze:
	@poetry run pip freeze
shell:
	@poetry shell
python:
	@poetry run ${PYTHON_CMD}


.PHONY: django-test test test-coverage dump-test-data
django-test:
	@echo "Run tests"
	@poetry run python3 manage.py test 
test:
	@echo "Run tests"
	@poetry run pytest -vv -s --cov-report term tests/test_*.py 
test-coverage:
	@echo "Run pytest"
	@poetry run pytest --cov-report html --cov-report term --cov=${PROJECT_NAME}
dump-test-data:
	@echo "Run dump test data"
	@poetry run python3 manage.py dumpdata api.actor api.movie api.movieactor > ./tests/initial_test_data.json


.PHONY: start start-gunicorn start-uvicorn
start:
	@echo "Start guicorn"
	@poetry run python manage.py runserver 8000
start-gunicorn:
	@echo "Start gnuicorn"
	${POETRY_CMD} -m gunicorn --reload monitora.asgi:application -k uvicorn.workers.UvicornWorker
start-uvicorn:
	@echo "Start debug"
	${POETRY_CMD} -m uvicorn monitora.asgi:application



.PHONY: migrate migration-generate database-recreate dump-movies
migrate:
	@echo "Run migrate database"
	${POETRY_CMD} manage.py migrate
migration-generate:
	${POETRY_CMD} manage.py makemigrations
database-recreate: database-recreate
	@echo "Run recreate database"
	${POETRY_CMD} manage.py sqlflush
	${POETRY_CMD} manage.py migrate
	$(MAKE migrate)
dump-movies:
	@echo "Run migrate database"
	${POETRY_CMD} manage.py dumpmovies --clear-database --count 300


.PHONY: docker-build docker-build-cache docker-run docker-sh docker-stop docker-remove docker-push docker-show-all
docker-build: check-lock
	$(call DOCKER_BUILD,--no-cache)
docker-build-cache:
	$(call DOCKER_BUILD)
docker-run:
	$(call DOCKER_RUN)
docker-sh:
	@echo "Run docker shell"
	$(call DOCKER_RUN,bash)
docker-stop:
	$(call DOCKER_STOP)
docker-remove:
	$(call DOCKER_REMOVE)
docker-push: check-lock
	$(call DOCKER_PUSH_TAG)
docker-show-all:
	$(call DOCKER_SHOW_IMAGES)


.PHONY: docker-compose-build docker-compose-build-cache docker-compose-up docker-compose-down docker-compose-run
docker-compose-data:
	@echo "Run build docker-compose"
	@if [ ! -d "${PG_DATA}" ]; then \
	(mkdir ${PG_DATA} && chown ${USER} ${PG_DATA} && chmod +rw ${PG_DATA} ) \
	fi
docker-compose-build: docker-build
	@echo "Run build docker-compose"
	@poetry run docker-compose build
docker-compose-build-cache: docker-build-cache
	@poetry run docker-compose build --no-cache
docker-compose-up: docker-compose-data
	@echo "Run docker-compose up"
	@poetry run docker-compose -p ${PROJECT_NAME} up
docker-compose-down:
	@echo "Down docker-compose"
	@poetry run docker-compose down
docker-compose-run: docker-compose-data
	@echo "Run docker-compose"
	@poetry run docker-compose run --rm $(subst -,_,${PROJECT_NAME})
