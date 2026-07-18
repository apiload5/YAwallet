# backend/apps/accounts/management/commands/create_admin.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Create admin user with proper arguments'

    def add_arguments(self, parser):
        parser.add_argument('--phone', type=str, help='Admin phone number')
        parser.add_argument('--password', type=str, help='Admin password')
        parser.add_argument('--name', type=str, help='Admin full name')

    def handle(self, *args, **options):
        # Get from environment or arguments
        phone = options.get('phone') or os.environ.get('ADMIN_PHONE', '03182724436')
        password = options.get('password') or os.environ.get('ADMIN_PASSWORD', 'Popup0921')
        full_name = options.get('name') or os.environ.get('ADMIN_NAME', 'Admin')

        # Check if user exists
        if User.objects.filter(phone=phone).exists():
            self.stdout.write(self.style.WARNING(f'⚠️ Admin with phone {phone} already exists'))
            return

        try:
            # Create superuser with correct arguments
            User.objects.create_superuser(
                phone=phone,
                full_name=full_name,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Admin created successfully!'))
            self.stdout.write(self.style.SUCCESS(f'   Phone: {phone}'))
            self.stdout.write(self.style.SUCCESS(f'   Name: {full_name}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to create admin: {str(e)}'))
