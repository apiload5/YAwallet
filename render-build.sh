#!/bin/bash

set -e  # Exit on error

echo "========================================"
echo "  YaWallet - Building Application"
echo "========================================"

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies (if any)
if [ -f package.json ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py makemigrations accounts
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser using existing command
echo "👤 Creating superuser..."
if python manage.py create_admin; then
    echo "✅ Superuser created successfully!"
else
    echo "⚠️ Superuser creation failed, continuing..."
fi

echo "========================================"
echo "✅ Build completed successfully!"
echo "========================================"
