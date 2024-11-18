# Leo backend with Django Setup

## Django Setup

1. `Pipenv install django` (create virtual environment including Django)
1. `Pipenv install` (setup virtual environment from existing Pipenv.lock)
2. `Pipenv shell` (to enter the virtual environment)

## Install Other Package Dependancies
1. `pip install -r requirements.txt`
    - requirements.txt can be subsequently updated (or created)
    - (venv) `pip freeze > requirements.txt`

## Project Creation
1. (venv) `django-admin startproject leo`

## App(s) Creation
1. (venv) `python manage.py startapp users`
2. (venv) `python manage.py startapp adhafera`

## Database Migration
1. (venv) `python manage.py makemigrations`
2. (venv) `python manage.py migrate`
3. (venv) `python manage.py createsuperuser`

## Serving - Development
1. `python manage.py runserver`

## Serving - Production
1. `gunicorn leo.wsgi`
