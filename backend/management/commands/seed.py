from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.db import transaction
from apps.accounts.models import User
from apps.wallet.models import Wallet
from apps.bills.models import Biller
from decimal import Decimal
import json

class Command(BaseCommand):
    help = 'Seed database with initial data'
    
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        
        # Create test user
        test_user, created = User.objects.get_or_create(
            phone='+923001234567',
            defaults={
                'full_name': 'Test User',
                'email': 'test@yawallet.com',
                'password': make_password('test1234'),
                'kyc_status': 'APPROVED',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Test user created'))
            
            # Set transaction PIN
            test_user.set_transaction_pin('1234')
            
            # Create wallet with initial balance
            wallet, wallet_created = Wallet.objects.get_or_create(
                user=test_user,
                defaults={'balance': Decimal('10000.00')}
            )
            
            if wallet_created:
                self.stdout.write(self.style.SUCCESS('Test wallet created with 10000 balance'))
        else:
            self.stdout.write(self.style.WARNING('Test user already exists'))
        
        # Create billers
        billers_data = [
            {
                'name': 'K-Electric',
                'code': 'KE',
                'category': 'ELECTRICITY',
                'icon': 'bolt',
                'color': '#FF6B6B',
                'consumer_number_format': 'KE-XXXXX'
            },
            {
                'name': 'Sui Gas',
                'code': 'SUI',
                'category': 'GAS',
                'icon': 'fire',
                'color': '#4ECDC4',
                'consumer_number_format': 'SUI-XXXXX'
            },
            {
                'name': 'PTCL Broadband',
                'code': 'PTCL',
                'category': 'INTERNET',
                'icon': 'wifi',
                'color': '#45B7D1',
                'consumer_number_format': 'PTCL-XXXXX'
            },
            {
                'name': 'Jazz Prepaid',
                'code': 'JAZZ',
                'category': 'TELEPHONE',
                'icon': 'phone',
                'color': '#FFA07A',
                'consumer_number_format': 'JZ-XXXXX'
            },
            {
                'name': 'University of Punjab',
                'code': 'PUNJAB',
                'category': 'EDUCATION',
                'icon': 'book',
                'color': '#98D8C8',
                'consumer_number_format': 'PU-XXXXX'
            },
        ]
        
        for biller_data in billers_data:
            biller, created = Biller.objects.get_or_create(
                code=biller_data['code'],
                defaults=biller_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created biller: {biller.name}'))
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed!'))
