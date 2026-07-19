#!/bin/bash
# render-build.sh

echo "========================================"
echo "  YaWallet - Building Application"
echo "========================================"

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Make migrations (CRITICAL!)
echo "🗄️ Making migrations..."
python manage.py makemigrations accounts
python manage.py makemigrations

# Run migrations (CRITICAL!)
echo "🗄️ Running migrations..."
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser
echo "👤 Creating superuser..."
python manage.py create_admin || true

echo "✅ Build completed!"
