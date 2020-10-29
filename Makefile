VIRTUAL_ENV ?= venv
NODE_BIN = node_modules/.bin
SOURCE_DIRS = adhocracy-plus apps tests
ARGUMENTS=$(filter-out $(firstword $(MAKECMDGOALS)), $(MAKECMDGOALS))

SED = sed
ifneq (, $(shell command -v gsed))
	SED = gsed
endif

.PHONY: all
all: help

.PHONY: help
help:
	@echo adhocracy+ development tools
	@echo
	@echo It will either use an exisiting virtualenv if it was entered
	@echo before or create a new one in the venv subdirectory.
	@echo
	@echo usage:
	@echo
	@echo "  make install         -- install dev setup"
	@echo "  make clean           -- delete node modules and venv"
	@echo "  make fixtures        -- load example data"
	@echo "  make server          -- start a dev server"
	@echo "  make watch           -- start a dev server and rebuild js and css files on changes"
	@echo "  make background      -- start background processes"
	@echo "  make test            -- run all test cases with pytest"
	@echo "  make test-lastfailed -- run test that failed last"
	@echo "  make test-clean      -- test on new database"
	@echo "  make coverage        -- write coverage report to dir htmlcov"
	@echo "  make lint            -- lint all project files"
	@echo "  make lint-quick      -- lint all files staged in git"
	@echo "  make po              -- create new po files from the source"
	@echo "  make po-fork         -- create new po files from the source on forked branches"
	@echo "  make compilemessages -- create new mo files from the translated po files"
	@echo "  make release         -- build everything required for a release"
	@echo

.PHONY: install
install:
	npm install --no-save
	npm run build
	if [ ! -f $(VIRTUAL_ENV)/bin/python3 ]; then python3 -m venv $(VIRTUAL_ENV); fi
	$(VIRTUAL_ENV)/bin/python3 -m pip install --upgrade -r requirements/dev.txt
	$(VIRTUAL_ENV)/bin/python3 manage.py migrate

.PHONY: clean
clean:
	if [ -f package-lock.json ]; then rm package-lock.json; fi
	if [ -d node_modules ]; then rm -rf node_modules; fi
	if [ -d venv ]; then rm -rf venv; fi

.PHONY: fixtures
fixtures:
	$(VIRTUAL_ENV)/bin/python3 manage.py loaddata adhocracy-plus/fixtures/site-dev.json
	$(VIRTUAL_ENV)/bin/python3 manage.py loaddata adhocracy-plus/fixtures/users-dev.json
	$(VIRTUAL_ENV)/bin/python3 manage.py loaddata adhocracy-plus/fixtures/orga-dev.json

.PHONY: server
server:
	$(VIRTUAL_ENV)/bin/python3 manage.py runserver 8004

.PHONY: watch
watch:
	trap 'kill %1' KILL; \
	npm run watch & \
	$(VIRTUAL_ENV)/bin/python3 manage.py runserver 8004

.PHONY: background
background:
	$(VIRTUAL_ENV)/bin/python3 manage.py process_tasks

.PHONY: test
test:
	$(VIRTUAL_ENV)/bin/py.test --reuse-db

.PHONY: test-lastfailed
test-lastfailed:
	$(VIRTUAL_ENV)/bin/py.test --reuse-db --last-failed

.PHONY: test-clean
test-clean:
	if [ -f test_db.sqlite3 ]; then rm test_db.sqlite3; fi
	$(VIRTUAL_ENV)/bin/py.test

.PHONY: coverage
coverage:
	$(VIRTUAL_ENV)/bin/py.test --reuse-db --cov --cov-report=html

.PHONY: lint
lint:
	EXIT_STATUS=0; \
	$(VIRTUAL_ENV)/bin/isort --diff -c $(SOURCE_DIRS) ||  EXIT_STATUS=$$?; \
	$(VIRTUAL_ENV)/bin/flake8 $(SOURCE_DIRS) --exclude migrations,settings ||  EXIT_STATUS=$$?; \
	npm run lint ||  EXIT_STATUS=$$?; \
	$(VIRTUAL_ENV)/bin/python manage.py makemigrations --dry-run --check --noinput || EXIT_STATUS=$$?; \
	exit $${EXIT_STATUS}

.PHONY: lint-quick
lint-quick:
	EXIT_STATUS=0; \
	npm run lint-staged ||  EXIT_STATUS=$$?; \
	$(VIRTUAL_ENV)/bin/python manage.py makemigrations --dry-run --check --noinput || EXIT_STATUS=$$?; \
	exit $${EXIT_STATUS}

.PHONY: lint-python-files
lint-python-files:
	EXIT_STATUS=0; \
	$(VIRTUAL_ENV)/bin/isort --df -c $(ARGUMENTS) || EXIT_STATUS=$$?; \
	$(VIRTUAL_ENV)/bin/flake8 $(ARGUMENTS) || EXIT_STATUS=$$?; \
	exit $${EXIT_STATUS}

.PHONY: po
po:
	$(VIRTUAL_ENV)/bin/python manage.py makemessages -d django --exclude locale-fork/locale --extension html,email,py
	$(VIRTUAL_ENV)/bin/python manage.py makemessages -d djangojs --exclude locale-fork/locale
	$(SED) -i 's%#: .*/adhocracy4%#: adhocracy4%' locale-source/locale/*/LC_MESSAGES/django*.po
	msgen locale-source/locale/en_GB/LC_MESSAGES/django.po -o locale-source/locale/en_GB/LC_MESSAGES/django.po
	msgen locale-source/locale/en_GB/LC_MESSAGES/djangojs.po -o locale-source/locale/en_GB/LC_MESSAGES/djangojs.po

.PHONY: po-fork
po-fork:
	$(VIRTUAL_ENV)/bin/python manage.py makemessages -d django --exclude locale-source/locale --extension html,email,py
	$(VIRTUAL_ENV)/bin/python manage.py makemessages -d djangojs --exclude locale-source/locale
	$(SED) -i 's%#: .*/adhocracy4%#: adhocracy4%' locale-fork/locale/*/LC_MESSAGES/django*.po
	msgen locale-fork/locale/en_GB/LC_MESSAGES/django.po -o locale-fork/locale/en_GB/LC_MESSAGES/django.po
	msgen locale-fork/locale/en_GB/LC_MESSAGES/djangojs.po -o locale-fork/locale/en_GB/LC_MESSAGES/djangojs.po

.PHONY: mo
mo:
	$(VIRTUAL_ENV)/bin/python manage.py compilemessages

.PHONY: tx-mo
tx-mo:
	$(VIRTUAL_ENV)/bin/tx pull -a
	$(VIRTUAL_ENV)/bin/python manage.py compilemessages

.PHONY: release
release: export DJANGO_SETTINGS_MODULE ?= adhocracy-plus.config.settings.build
release:
	npm install --silent
	npm run build:prod
	$(VIRTUAL_ENV)/bin/python3 -m pip install -r requirements.txt -q
	$(VIRTUAL_ENV)/bin/python3 manage.py compilemessages -v0
	$(VIRTUAL_ENV)/bin/python3 manage.py collectstatic --noinput -v0
