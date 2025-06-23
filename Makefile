VIRTUAL_ENV ?= venv
NODE_BIN = node_modules/.bin
SOURCE_DIRS = adhocracy-plus apps tests
ARGUMENTS=$(filter-out $(firstword $(MAKECMDGOALS)), $(MAKECMDGOALS))

# for mac os gsed is needed (brew install gnu-sed and brew install gsed)
SED = sed
ifneq (, $(shell command -v gsed;))
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
	@echo "  make install					-- install dev setup"
	@echo "  make clean						-- delete node modules and venv"
	@echo "  make fixtures					-- load example data"
	@echo "  make server					-- start a dev server"
	@echo "  make watch						-- start a dev server and rebuild js and css files on changes"
	@echo "  make background				-- start background processes"
	@echo "  make test						-- run all test cases"
	@echo "  make pytest					-- run all test cases with pytest"
	@echo "  make pytest-lastfailed			-- run test that failed last"
	@echo "  make pytest-clean				-- test on new database"
	@echo "  make jstest					-- run js tests with coverage"
	@echo "  make jstest-nocov				-- run js tests without coverage"
	@echo "  make jstest-debug				-- run changed tests only, no coverage"
	@echo "  make jstest-updateSnapshots	-- update jest snapshots"
	@echo "  make coverage					-- write coverage report to dir htmlcov"
	@echo "  make lint						-- lint all project files"
	@echo "  make lint-quick				-- lint all files staged in git"
	@echo "  make lint-js-fix				-- fix linting for all js files staged in git"
	@echo "  make lint-html-fix				-- fix linting for all html files passed as argument"
	@echo "  make lint-html-files			-- lint for all html files with django profile rules"
	@echo "  make lint-python-files			-- lint all python files passed as argument"
	@echo "  make po						-- create new po files from the source"
	@echo "  make mo						-- create new mo files from the translated po files"
	@echo "  make release					-- build everything required for a release"
	@echo "  make postgres-start			-- start the local postgres cluster"
	@echo "  make postgres-stop				-- stops the local postgres cluster"
	@echo "  make postgres-create			-- create the local postgres cluster (only works on ubuntu 20.04)"
	@echo "  make local-a4					-- patch to use local a4 (needs to have path ../adhocracy4)"
	@echo "  make celery-worker-start		-- starts the celery worker in the foreground"
	@echo "  make celery-worker-status		-- lists all registered tasks and active worker nodes"
	@echo "  make celery-worker-dummy-task	-- calls the dummy task and prints result from redis"
	@echo "  make docs                   	-- run the mkdocs server for the documentation"
	@echo

.PHONY: install
install:
	npm install --no-save
	npm run build
	if [ ! -f $(VIRTUAL_ENV)/bin/python3 ]; then python3 -m venv $(VIRTUAL_ENV); fi
	$(VIRTUAL_ENV)/bin/python -m pip install --upgrade -r requirements/dev.txt
	$(VIRTUAL_ENV)/bin/python manage.py migrate

.PHONY: clean
clean:
	if [ -f package-lock.json ]; then rm package-lock.json; fi
	if [ -d node_modules ]; then rm -rf node_modules; fi
	if [ -d venv ]; then rm -rf venv; fi

.PHONY: fixtures
fixtures:
	$(VIRTUAL_ENV)/bin/python manage.py loaddata adhocracy-plus/fixtures/site-dev.json
	$(VIRTUAL_ENV)/bin/python manage.py loaddata adhocracy-plus/fixtures/users-dev.json
	$(VIRTUAL_ENV)/bin/python manage.py loaddata adhocracy-plus/fixtures/orga-dev.json

.PHONY: server
server:
	$(VIRTUAL_ENV)/bin/python manage.py runserver 8004

.PHONY: watch
watch:
	trap 'kill %1' KILL; \
	npm run watch & \
	$(VIRTUAL_ENV)/bin/python manage.py runserver 8004

.PHONY: background
background:
	$(VIRTUAL_ENV)/bin/python manage.py process_tasks

.PHONY: test
test:
	$(VIRTUAL_ENV)/bin/py.test --reuse-db
	npm run testNoCov

.PHONY: pytest
pytest:
	$(VIRTUAL_ENV)/bin/py.test --reuse-db

.PHONY: pytest-lastfailed
pytest-lastfailed:
	$(VIRTUAL_ENV)/bin/py.test --reuse-db --last-failed

.PHONY: pytest-clean
pytest-clean:
	if [ -f test_db.sqlite3 ]; then rm test_db.sqlite3; fi
	$(VIRTUAL_ENV)/bin/py.test

.PHONY: jstest
jstest:
	npm run test

.PHONY: jstest-nocov
jstest-nocov:
	npm run testNoCov

.PHONY: jstest-debug
jstest-debug:
	npm run testDebug

.PHONY: jstest-updateSnapshots
jstest-updateSnapshots:
	npm run updateSnapshots

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

.PHONY: lint-js-fix
lint-js-fix:
	EXIT_STATUS=0; \
	npm run lint-fix ||  EXIT_STATUS=$$?; \
	exit $${EXIT_STATUS}

# Use with caution, the automatic fixing might produce bad results
.PHONY: lint-html-fix
lint-html-fix:
	EXIT_STATUS=0; \
	$(VIRTUAL_ENV)/bin/djlint $(ARGUMENTS) --reformat --profile=django || EXIT_STATUS=$$?; \
	exit $${EXIT_STATUS}

.PHONY: lint-html-files
lint-html-files:
	EXIT_STATUS=0; \
	$(VIRTUAL_ENV)/bin/djlint $(ARGUMENTS) --profile=django --ignore=H006,H030,H031,H037,T002 || EXIT_STATUS=$$?; \
	exit $${EXIT_STATUS}

.PHONY: lint-python-files
lint-python-files:
	EXIT_STATUS=0; \
	$(VIRTUAL_ENV)/bin/black $(ARGUMENTS) || EXIT_STATUS=$$?; \
	$(VIRTUAL_ENV)/bin/isort $(ARGUMENTS) --filter-files || EXIT_STATUS=$$?; \
	$(VIRTUAL_ENV)/bin/flake8 $(ARGUMENTS) || EXIT_STATUS=$$?; \
	exit $${EXIT_STATUS}

.PHONY: po
po:
	$(VIRTUAL_ENV)/bin/python manage.py makemessages --all --no-obsolete -d django --extension html,email,py --ignore '$(CURDIR)/node_modules/adhocracy4/adhocracy4/*'
	$(VIRTUAL_ENV)/bin/python manage.py makemessages --all --no-obsolete -d djangojs --ignore '$(VIRTUAL_ENV)/*' --ignore '$(CURDIR)/node_modules/dsgvo-video-embed/dist/*'
	$(foreach file, $(wildcard locale-*/locale/*/LC_MESSAGES/django*.po), \
		$(SED) -i 's%#: .*/adhocracy4%#: adhocracy4%' $(file);)
	$(foreach file, $(wildcard locale-*/locale/*/LC_MESSAGES/django*.po), \
		$(SED) -i 's%#: .*/dsgvo-video-embed/js%#: dsgvo-video-embed/js%' $(file);)
	msgen locale-source/locale/en/LC_MESSAGES/django.po -o locale-source/locale/en/LC_MESSAGES/django.po
	msgen locale-source/locale/en/LC_MESSAGES/djangojs.po -o locale-source/locale/en/LC_MESSAGES/djangojs.po

.PHONY: mo
mo:
	$(VIRTUAL_ENV)/bin/python manage.py compilemessages

.PHONY: release
release: export DJANGO_SETTINGS_MODULE ?= adhocracy-plus.config.settings.build
release:
	npm install --silent
	npm run build:prod
	$(VIRTUAL_ENV)/bin/python -m pip install -r requirements.txt -q
	$(VIRTUAL_ENV)/bin/python manage.py compilemessages -v0
	$(VIRTUAL_ENV)/bin/python manage.py collectstatic --noinput -v0

.PHONY: postgres-start
postgres-start:
	sudo systemctl start postgresql

.PHONY: postgres-stop
postgres-stop:
	sudo systemctl stop postgresql

.PHONY: postgres-create
postgres-create:
	@if ! command -v psql > /dev/null 2>&1; then \
		echo "PostgreSQL is not installed. Please install it with 'sudo apt install postgresql'"; \
		exit 1; \
	fi
	@if ! sudo systemctl is-active --quiet postgresql; then \
		echo "PostgreSQL service is not running. Starting it..."; \
		sudo systemctl start postgresql; \
		sleep 2; \
	fi
	sudo -u postgres createuser --createdb --no-createrole --no-superuser django || true
	sudo -u postgres createdb --owner=django --encoding=UTF8 django || true
	sudo -u postgres psql -U postgres -d django -c "CREATE EXTENSION postgis;" || true

.PHONY: local-a4
local-a4:
	if [ -d "../adhocracy4" ]; then \
		$(VIRTUAL_ENV)/bin/python -m pip install --upgrade ../adhocracy4; \
		$(VIRTUAL_ENV)/bin/python manage.py migrate; \
		npm link ../adhocracy4; \
	fi

.PHONY: celery-worker-start
celery-worker-start:
	$(VIRTUAL_ENV)/bin/celery --app adhocracy-plus worker --loglevel INFO

.PHONY: celery-worker-status
celery-worker-status:
	$(VIRTUAL_ENV)/bin/celery --app adhocracy-plus inspect registered

.PHONY: celery-worker-dummy-task
celery-worker-dummy-task:
	$(VIRTUAL_ENV)/bin/celery --app adhocracy-plus call dummy_task | awk '{print "celery-task-meta-"$$0}' | xargs redis-cli get | python3 -m json.tool

.PHONY: docs
docs:
	$(VIRTUAL_ENV)/bin/mkdocs serve
