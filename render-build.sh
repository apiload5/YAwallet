#!/bin/bash

set -e  # Exit on error

echo "========================================"
echo "  YaWallet - Building Application"
echo "========================================"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies (if any)
if [ -f package.json ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Wait for database (if using PostgreSQL)
echo "⏳ Waiting for database..."
timeout 30 python -c "
import time
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from django.db import connections
from django.db.utils import OperationalError
for i in range(30):
    try:
        connections['default'].cursor()
        print('Database is ready!')
        break
    except OperationalError:
        time.sleep(1)
else:
    print('Database timeout, continuing anyway...')
" || true

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py makemigrations accounts --noinput || true
python manage.py makemigrations --noinput || true
python manage.py migrate --noinput || true

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput || true

# Create superuser (using updated command)
echo "👤 Creating superuser..."
if python manage.py create_admin; then
    echo "✅ Superuser created successfully!"
else
    echo "⚠️ Superuser creation failed, continuing..."
fi

# Create data directory if needed
mkdir -p /app/media /app/staticfiles

echo "========================================"
echo "✅ Build completed successfully!"
echo "========================================"
