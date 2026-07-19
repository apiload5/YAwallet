#!/bin/bash

echo "========================================"
echo "  YaWallet - Building Application"
echo "========================================"

# Exit on error
set -e

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️ DATABASE_URL not set, using SQLite"
else
    echo "✅ DATABASE_URL found: ${DATABASE_URL%%@*}@***"
fi

# Run migrations
echo "🗄️ Running migrations..."
python manage.py makemigrations accounts --noinput || true
python manage.py makemigrations --noinput || true
python manage.py migrate --noinput || true

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --no-post-process || true

# Create superuser
echo "👤 Creating superuser..."
python manage.py create_admin || echo "⚠️ Superuser creation failed"

echo "========================================"
echo "✅ Build completed!"
echo "========================================"
