release: python manage.py migrate
web: gunicorn config.wsgi:application
metrics: python manage.py start_metrics_server
