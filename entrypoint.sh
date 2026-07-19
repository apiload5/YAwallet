#!/bin/bash
# entrypoint.sh

echo "========================================"
echo "  YaWallet - Starting Application"
echo "========================================"

# Always run migrations before starting
echo "🗄️ Running migrations..."
python manage.py makemigrations accounts --noinput || true
python manage.py makemigrations --noinput || true
python manage.py migrate --noinput || true

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput || true

# Create superuser
echo "👤 Creating superuser..."
python manage.py create_admin || true

echo "✅ Application ready!"
exec "$@"
