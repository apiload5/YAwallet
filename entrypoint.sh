#!/bin/sh
set -e

echo "========================================"
echo "  YaWallet - Starting Application"
echo "========================================"

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
fi

echo "========================================"
echo "  ✓ YaWallet is ready!"
echo "========================================"

# Start the application
exec "$@"
