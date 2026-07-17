from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create admin user'

    def handle(self, *args, **options):
        if not User.objects.filter(phone='+923182724436').exists():
            User.objects.create_superuser(
                phone='+923182724436',
                full_name='Amir',
                password='Popup0921'
            )
            self.stdout.write(self.style.SUCCESS('✅ Admin created!'))
            self.stdout.write('Phone: +923182724436')
            self.stdout.write('Password: Popup0921')
        else:
            self.stdout.write(self.style.WARNING('⚠️ Admin already exists'))
