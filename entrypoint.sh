#!/bin/sh
set -e

echo "========================================"
echo "  YaWallet - Starting Application"
echo "========================================"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "========================================"
echo "  ✓ YaWallet is ready!"
echo "========================================"

exec "$@"
