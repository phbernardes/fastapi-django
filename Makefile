.EXPORT_ALL_VARIABLES:
PIPENV_VENV_IN_PROJECT=1
ISORT=.venv/bin/isort
FLAKE8=.venv/bin/flake8

venv:  ## Create local virtual env
	rm -rf venv .venv
	pip install pipenv
	pipenv sync --dev

db:  ## Create database and superuser (admin/admin)
	pipenv run ./manage.py migrate; 
	pipenv run DJANGO_SUPERUSER_PASSWORD=admin ./manage.py createsuperuser --username admin --email admin@test.com --no-input

run:  ## Run server on 127.0.0.1:8000
	pipenv run uvicorn fastdjango.asgi:app --reload

tree:  ## Show directory tree
	tree -I 'Pipfile*|Makefile|blackcfg.toml|setup.cfg|static|db.sqlite3|*__pycache__*'

.SILENT: tree venv
