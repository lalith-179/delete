from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Account

class Command(BaseCommand):
    help = 'Creates a default superuser for the application'

    def handle(self, *args, **options):
        User = get_user_model()
        
        if not User.objects.filter(email='admin@example.com').exists():
            self.stdout.write('Creating default superuser...')
            
            # Create superuser with is_admin=True
            admin_user = User.objects.create_user(
                username='admin',  # Adding username parameter
                email='admin@example.com',
                first_name='Admin',
                last_name='User',
                password='Admin@123',
                is_admin=True,
                is_staff=True,
                is_active=True,
                is_superuser=True
            )
            
            self.stdout.write(self.style.SUCCESS('Default superuser created successfully!'))
            self.stdout.write(self.style.SUCCESS('Email: admin@example.com'))
            self.stdout.write(self.style.SUCCESS('Password: Admin@123'))
        else:
            self.stdout.write(self.style.WARNING('Default superuser already exists.'))
