#set -e
#sleep 5

#python manage.py migrate

#python manage.py runserver 0.0.0.0:8000

#exec "$@"

#!/bin/sh
set -e

echo "Waiting for Postgres..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Postgres is up - continuing"

python manage.py migrate
python manage.py collectstatic --noinput

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
