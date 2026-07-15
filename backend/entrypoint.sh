#!/bin/sh

# Wait for postgres
echo "Waiting for postgres..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

# Run migrations
python manage.py migrate --noinput

# Collect static
python manage.py collectstatic --noinput

# Start gunicorn
exec "$@"
