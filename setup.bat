@echo off
REM Activate virtual environment
call venv\Scripts\activate

REM Install Django and dependencies
pip install django django-cors-headers

REM Apply migrations
python manage.py makemigrations
python manage.py migrate

REM Create superuser (optional, for admin panel)
python manage.py createsuperuser

REM Run server
python manage.py runserver