#!/bin/sh
set -e

echo "========================================"
echo "  YaWallet - Starting Application"
echo "========================================"

# ============================================
# CLEAN START - REMOVE OLD DB IF CORRUPTED
# ============================================
if [ "${RESET_DB:-false}" = "true" ]; then
    echo "🗑️  Resetting database..."
    rm -f /app/db.sqlite3
fi

# ============================================
# RUN MIGRATIONS
# ============================================
echo "Running migrations..."
python manage.py makemigrations accounts
python manage.py makemigrations
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# ============================================
# CREATE ADMIN
# ============================================
echo "Creating superuser..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
phone = '+923182724436'
if not User.objects.filter(phone=phone).exists():
    User.objects.create_superuser(phone, '', 'Popup0921')
    print('✅ Superuser created!')
else:
    print('⚠️ Superuser already exists')
EOF

echo "========================================"
echo "  ✓ YaWallet is ready!"
echo "========================================"

exec "$@"
