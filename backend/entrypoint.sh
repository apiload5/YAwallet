#!/bin/sh
set -e

echo "========================================"
echo "  YaWallet - Starting Application"
echo "========================================"

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do
  sleep 0.5
done
echo "✓ PostgreSQL started"

# Wait for Redis
echo "Waiting for Redis..."
while ! nc -z ${REDIS_HOST:-redis} ${REDIS_PORT:-6379}; do
  sleep 0.5
done
echo "✓ Redis started"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput
echo "✓ Migrations completed"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput
echo "✓ Static files collected"

# Seed database (if enabled)
if [ "${SEED_DATABASE:-false}" = "true" ]; then
    echo "Seeding database..."
    python manage.py seed
    echo "✓ Database seeded"
fi

echo "========================================"
echo "  ✓ YaWallet is ready!"
echo "========================================"

# Start the application
exec "$@"
