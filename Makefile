.PHONY: print-env \
        init \
        install-update \
        install-package \
        virtualenv \
        clean \
        recreate-db \
        load-dev-data \
        manage \
        run \
        shell \
        test \
        coverage \

.DEFAULT_GOAL := run

PROJECT_NAME = traq
VENV_DIR ?= .env
export PATH := $(VENV_DIR)/bin:$(PATH)
MANAGE = ./manage.py

print-env:
	@echo PROJECT_NAME: $(PROJECT_NAME)
	@echo VENV_DIR: $(VENV_DIR)
	@echo MANAGE: $(MANAGE)

init: $(VENV_DIR)
	@$(MAKE) recreate-db
	@$(MAKE) load-dev-data
	@$(MANAGE) test

install: $(VENV_DIR)
	$(MANAGE) migrate
	$(MANAGE) loaddata initial_data
	$(MANAGE) collectstatic --noinput
	touch traq/wsgi.py

install-update: $(VENV_DIR)
	pip install -U -r requirements.txt

# pip install $(args)
# Examples:
#     make install-package args=bpython
#     make install-package args='pep8 pyflakes'
#     make install-package args='-U pep8'
install-package: $(VENV_DIR)
	pip install $(args)

$(VENV_DIR): requirements.txt
	@if [ -d "$(VENV_DIR)" ]; then \
	    echo "Directory exists: $(VENV_DIR)"; \
	    exit 1; \
	fi
	python3 -m venv $(VENV_DIR)
	curl https://bootstrap.pypa.io/get-pip.py | python3
	pip install -r requirements.txt

# remove pyc junk
clean:
	find . -iname "*.pyc" -delete
	find . -iname "*.pyo" -delete
	find . -iname "__pycache__" -delete

recreate-db: $(VENV_DIR)
	mysql -u root -e 'drop database $(PROJECT_NAME);' || true
	mysql -u root -e 'create database $(PROJECT_NAME);'
	$(MANAGE) migrate --noinput
	$(MANAGE) loaddata initial_data

load-dev-data: $(VENV_DIR)
	$(MANAGE) loaddata dev_data

## Django (wrappers for ./manage.py commands)

# Run a manage.py command
#
# This is here so we don't have to create a target for every single manage.py
# command. Of course, you could also just source your virtualenv's bin/activate
# script and run manage.py directly, but this provides consistency if you're in
# the habit of using make.
#
# Examples:
#     make manage args=migrate
#     make manage args='runserver 8080'
manage: $(VENV_DIR)
	@$(MANAGE) $(args)

# run the django web server
host ?= 0.0.0.0
port ?= 8000
run: $(VENV_DIR)
	$(MANAGE) runserver $(host):$(port)

# start a django shell
# run `make install-package name=bpython` (or ipython) first if you want
# a fancy shell
shell: $(VENV_DIR)
	$(MANAGE) shell $(args)

# run the unit tests
# use `make test test=path.to.test` if you want to run a specific test
test: $(VENV_DIR)
	$(MANAGE) test $(test)

# run the unit tests with coverage.
# go to `0.0.0.0:8000/htmlcov/index.html` to view test coverage
coverage: $(VENV_DIR)
	coverage run ./manage.py test $(test) && coverage html --omit=.env/*

## /Django
