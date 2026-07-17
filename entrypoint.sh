#!/bin/sh
set -e

echo "========================================"
echo "  YaWallet - Starting Application"
echo "========================================"

echo "Running migrations..."
python /app/manage.py migrate --noinput

echo "Collecting static files..."
python /app/manage.py collectstatic --noinput

# ============================================
# AUTO-CREATE ADMIN - IN ROOT ENTRYPOINT
# ============================================
echo "Creating superuser..."
python /app/manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
phone = '+923182724436';
if not User.objects.filter(phone=phone).exists():
    User.objects.create_superuser(phone, '', 'Amir')
    print('✅ Superuser created! Phone: +923182724436, Password: Popup0921')
else:
    print('⚠️ Superuser already exists')
"

echo "========================================"
echo "  ✓ YaWallet is ready!"
echo "========================================"

exec "$@"
