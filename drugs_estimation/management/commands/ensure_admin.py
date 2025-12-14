from django.core.management.base import BaseCommand
from drugs_estimation.redis_client import redis_user_client


class Command(BaseCommand):
    help = 'Ensure admin user exists in Redis with superuser privileges'

    def handle(self, *args, **options):
        admin_user = redis_user_client.get_user('admin')
        
        if admin_user:
            is_superuser = admin_user.get('is_superuser') in ['1', 'True', True]
            self.stdout.write('Admin user exists in Redis')
            self.stdout.write(f"  Username: {admin_user.get('username')}")
            self.stdout.write(f"  Email: {admin_user.get('email')}")
            self.stdout.write(f"  Is superuser: {is_superuser}")
            
            # Update admin to ensure superuser status
            if not is_superuser:
                self.stdout.write('Updating admin user to have superuser privileges...')
                redis_user_client.redis_client.hset('user:admin', 'is_superuser', '1')
                redis_user_client.redis_client.hset('user:admin', 'is_staff', '1')
                self.stdout.write(self.style.SUCCESS('Admin user updated to superuser'))
            else:
                self.stdout.write(self.style.SUCCESS('Admin user already has superuser privileges'))
        else:
            self.stdout.write('Creating admin user in Redis...')
            admin_user = redis_user_client.register_user(
                username='admin',
                password='admin123',
                email='admin@example.com',
                first_name='Admin',
                last_name='User',
                is_staff=True,
                is_superuser=True
            )
            
            if admin_user:
                self.stdout.write(self.style.SUCCESS('Admin user created successfully'))
                self.stdout.write(f"  Username: admin")
                self.stdout.write(f"  Password: admin123")
            else:
                self.stdout.write(self.style.ERROR('Failed to create admin user'))
