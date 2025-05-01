import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates an admin user with all permissions'

    def handle(self, *args, **options):
        User = get_user_model()
        try:
            # Delete existing admin user if exists
            User.objects.filter(username='admin').delete()
            
            # Set default admin credentials
            username = 'admin'
            email = 'admin@example.com'
            password = 'Admin@123'

            # Create new admin user
            admin = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()
            
            self.stdout.write(self.style.SUCCESS('Admin user created successfully!'))
            self.stdout.write('Default admin credentials:')
            self.stdout.write('Username: ' + username)
            self.stdout.write('Password: ' + password)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating admin user: {str(e)}'))