set shell := ["powershell", "-c"]

python := "python"
manage := "python manage.py"

default:
	@just --list

dev port:
    {{manage}} runserver {{port}}

new_app name:
    {{manage}} startapp {{name}}

migrate:
	{{manage}} makemigrations
	{{manage}} migrate

admin:
	{{manage}} createsuperuser