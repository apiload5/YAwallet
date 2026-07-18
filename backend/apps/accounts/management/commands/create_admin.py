# backend/apps/accounts/management/commands/create_admin.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class Command(BaseCommand):
    help = 'Create admin user with proper arguments'

    def add_arguments(self, parser):
        parser.add_argument('--phone', type=str, help='Admin phone number')
        parser.add_argument('--password', type=str, help='Admin password')
        parser.add_argument('--name', type=str, help='Admin full name')

    def handle(self, *args, **options):
        # Get from environment or arguments
        phone = options.get('phone') or os.environ.get('ADMIN_PHONE', '923001234567')
        password = options.get('password') or os.environ.get('ADMIN_PASSWORD', 'admin123')
        full_name = options.get('name') or os.environ.get('ADMIN_NAME', 'Admin')

        self.stdout.write(f'📱 Creating admin with phone: {phone}')

        # Check if user exists
        if User.objects.filter(phone=phone).exists():
            self.stdout.write(self.style.WARNING(f'⚠️ Admin with phone {phone} already exists'))
            return

        try:
            # Try different approaches for superuser creation
            try:
                # Method 1: Standard create_superuser
                User.objects.create_superuser(
                    phone=phone,
                    full_name=full_name,
                    password=password
                )
            except TypeError:
                # Method 2: If UserManager expects different arguments
                try:
                    User.objects.create_superuser(
                        phone=phone,
                        password=password
                    )
                except TypeError:
                    # Method 3: Create user then mark as superuser
                    user = User.objects.create_user(
                        phone=phone,
                        full_name=full_name,
                        password=password
                    )
                    user.is_superuser = True
                    user.is_staff = True
                    user.save()
            
            self.stdout.write(self.style.SUCCESS(f'✅ Admin created successfully!'))
            self.stdout.write(self.style.SUCCESS(f'   Phone: {phone}'))
            self.stdout.write(self.style.SUCCESS(f'   Name: {full_name}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to create admin: {str(e)}'))
            logger.error(f'Admin creation failed: {str(e)}')
            raise
