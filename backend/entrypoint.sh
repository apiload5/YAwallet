#!/bin/sh
set -e

echo "========================================"
echo "  YaWallet - Starting Application"
echo "========================================"

# Wait for postgres to be ready
echo "Waiting for postgres..."
while ! nc -z db 5432; do
  sleep 0.5
done
echo "PostgreSQL is up - starting"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Seed database (if enabled)
if [ "${SEED_DATABASE:-false}" = "true" ]; then
    echo "Seeding database..."
    python manage.py seed
fi  # <-- ye missing tha

echo "========================================"
echo "  ✓ YaWallet is ready!"
echo "========================================"

# Start the application
exec "$@"
