release: python manage.py migrate
web: gunicorn code_shot.wsgi:application --bind 0.0.0.0:$PORT
