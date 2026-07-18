#!/bin/bash

echo "========================================"
echo "  YaWallet - Starting Application"
echo "========================================"

# Set Django settings module
export DJANGO_SETTINGS_MODULE=settings

# Wait for database (if using PostgreSQL)
if [ -n "$DATABASE_URL" ]; then
    echo "⏳ Waiting for database..."
    # Extract host and port from DATABASE_URL
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):\([0-9]*\)\/.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):\([0-9]*\)\/.*/\2/p')
    
    if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
        while ! nc -z $DB_HOST $DB_PORT; do
            sleep 1
        done
        echo "✅ Database is ready!"
    fi
fi

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
echo "✅ Application is ready!"
echo "========================================"

# Execute the main command
exec "$@"
