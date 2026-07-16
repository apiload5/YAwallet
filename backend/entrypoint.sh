#!/bin/sh
set -e

echo "========================================"
echo "  YaWallet - Starting Application"
echo "========================================"

# Wait for PostgreSQL (using python)
if [ -n "$DB_HOST" ]; then
    echo "Waiting for PostgreSQL..."
    python -c "
import time
import os
import socket
host = os.environ.get('DB_HOST', 'db')
port = int(os.environ.get('DB_PORT', 5432))
while True:
    try:
        socket.create_connection((host, port), timeout=5)
        break
    except:
        print('Waiting for database...')
        time.sleep(1)
"
    echo "✓ PostgreSQL started"
fi

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Seed database (if enabled)
if [ "${SEED_DATABASE:-false}" = "true" ]; then
    echo "Seeding database..."
    python manage.py seed || echo "Seed script not found, skipping..."
fi

echo "========================================"
echo "  ✓ YaWallet is ready!"
echo "========================================"

# Start the application
exec "$@"
