VENV_NAME=.venv
PYTHON=${VENV_NAME}/bin/python3

include .env
export

up:
	docker-compose up -d

up_recreate:
	docker-compose up -d --force-recreate

start:
	docker-compose start

stop:
	docker-compose stop

build:
	docker-compose build
	docker-compose create

logs:
	docker-compose logs -f --tail=100

token:
	@NEW_TOKEN=$$(yc iam create-token --format json | jq -r '.iam_token'); \
	sed -i 's/^IAM_TOKEN=.*$$/IAM_TOKEN='"$$NEW_TOKEN"'/' .env

test:
	docker-compose up test

flake8:
	$(PYTHON) -m flake8 ./app

mypy:
	$(PYTHON) -m mypy ./app

_venv:
	test -d $(VENV_NAME) || virtualenv -p python3 $(VENV_NAME) && make _install

_install:
	${PYTHON} -m pip install -r requirements.txt
