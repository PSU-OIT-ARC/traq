.PHONY: print-env \
        init \
        install \
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
		love \

.DEFAULT_GOAL := run

PROJECT_NAME = traq
VENV_DIR ?= .env
BIN_DIR = $(VENV_DIR)/bin
PYTHON = $(BIN_DIR)/python
PIP = $(BIN_DIR)/pip
MANAGE = $(PYTHON) manage.py
SETTINGS_MODULE = $(DJANGO_SETTINGS_MODULE)
ifeq ($(strip $(SETTINGS_MODULE)),)
SETTINGS_MODULE = $(PROJECT_NAME).settings
endif

print-env:
	@echo PROJECT_NAME: $(PROJECT_NAME)
	@echo VENV_DIR: $(VENV_DIR)
	@echo BIN_DIR: $(BIN_DIR)
	@echo PYTHON: $(PYTHON)
	@echo PIP: $(PIP)
	@echo MANAGE: $(MANAGE)

init:
	@$(MAKE) virtualenv args='-p python3'
	cp ./traq/demo_settings.py ./traq/local_settings.py
	@$(MAKE) recreate-db
	@$(MAKE) load-dev-data
	@$(MANAGE) test

install:
	$(PIP) install -r requirements.txt

install-update:
	$(PIP) install -U -r requirements.txt

# pip install $(args)
# Examples:
#     make install-package args=bpython
#     make install-package args='pep8 pyflakes'
#     make install-package args='-U pep8'
install-package:
	$(PIP) install $(args)

virtualenv:
	@if [ -d "$(VENV_DIR)" ]; then \
	    echo "Directory exists: $(VENV_DIR)"; \
	    exit 1; \
	fi
	virtualenv $(args) $(VENV_DIR)
	@echo
	$(MAKE) install

# remove pyc junk
clean:
	find . -iname "*.pyc" -delete
	find . -iname "*.pyo" -delete
	find . -iname "__pycache__" -delete

recreate-db:
	mysql -u root -e 'drop database $(PROJECT_NAME);' || true
	mysql -u root -e 'create database $(PROJECT_NAME);'
	mysql -u root -e 'create user $(PROJECT_NAME)@"localhost";'|| true
	mysql -u root -e 'grant all privileges on $(PROJECT_NAME).* to $(PROJECT_NAME)@"localhost"; FLUSH PRIVILEGES;'
	$(MANAGE) syncdb
	$(MANAGE) migrate
	$(MANAGE) loaddata initial_data

load-dev-data:
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
manage:
	@$(MANAGE) $(args)

# run the django web server
host ?= 0.0.0.0
port ?= 8000
run:
	$(MANAGE) runserver $(host):$(port)

# start a django shell
# run `make install-package name=bpython` (or ipython) first if you want
# a fancy shell
shell:
	$(MANAGE) shell $(args)

# run the unit tests
# use `make test test=path.to.test` if you want to run a specific test
test:
	$(MANAGE) test $(test)

# run the unit tests with coverage. 
# go to `0.0.0.0:8000/htmlcov/index.html` to view test coverage
coverage:
	coverage run ./manage.py test $(test) && coverage html

love:
	@echo Not war?

## /Django
