#!/bin/bash

echo "========================================"
echo "  YaWallet - Starting Application"
echo "========================================"

# Check database
echo "🔍 Checking database connection..."
if [ -n "$DATABASE_URL" ]; then
    echo "✅ DATABASE_URL found"
else
    echo "⚠️ DATABASE_URL not found, using SQLite"
fi

# Run migrations before starting
echo "🗄️ Running migrations..."
python manage.py migrate --noinput || echo "⚠️ Migrations failed"

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --no-post-process || echo "⚠️ Static files collection failed"

# Create superuser
echo "👤 Creating superuser..."
python manage.py create_admin || echo "⚠️ Superuser creation failed"

echo "========================================"
echo "✅ Application ready!"
echo "========================================"

# Start the application
exec "$@"
