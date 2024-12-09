from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os

class Command(BaseCommand):
    help = 'Create or update a superuser'

    def handle(self, *args, **kwargs):
        username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'adminpass')

        user, created = User.objects.update_or_create(
            username=username,
            defaults={
                'email': email,
                'is_superuser': True,
                'is_staff': True
            }
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(f"Superuser {username} created.")
        else:
            if password:
                user.set_password(password)
            user.save()
            self.stdout.write(f"Superuser {username} updated with new details.")
