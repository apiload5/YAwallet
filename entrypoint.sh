#!/bin/sh
set -e

echo "========================================"
echo "  YaWallet - Starting Application"
echo "========================================"

# Debug: Show what's in /app
echo "Files in /app:"
ls -la /app/

echo "Files in /app/yawallet:"
ls -la /app/yawallet/ || echo "yawallet folder not found!"

echo "Running migrations..."
python /app/manage.py migrate --noinput

echo "Collecting static files..."
python /app/manage.py collectstatic --noinput

echo "========================================"
echo "  ✓ YaWallet is ready!"
echo "========================================"

exec "$@"
