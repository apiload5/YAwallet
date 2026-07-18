#!/bin/bash

echo "========================================"
echo "  YaWallet - Building Application"
echo "========================================"

# Exit on error
set -e

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install system dependencies for Django
echo "🔧 Installing system dependencies..."
apt-get update && apt-get install -y \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/* || true

# Run migrations
echo "🗄️ Running migrations..."
python manage.py makemigrations accounts --noinput || true
python manage.py makemigrations --noinput || true
python manage.py migrate --noinput || true

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput || true

# Create superuser
echo "👤 Creating superuser..."
if python manage.py create_admin 2>/dev/null; then
    echo "✅ Superuser created successfully!"
else
    echo "⚠️ Superuser creation failed or already exists"
fi

echo "========================================"
echo "✅ Build completed successfully!"
echo "========================================"
