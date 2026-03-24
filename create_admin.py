import os
import django
from getpass import getpass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saarthi.settings')
django.setup()

from django.contrib.auth.models import User

# Get credentials from environment or prompt user
username = os.environ.get('ADMIN_USERNAME') or input("Enter admin username: ")
email = os.environ.get('ADMIN_EMAIL') or input("Enter admin email: ")
if not os.environ.get('ADMIN_PASSWORD'):
    password = getpass("Enter admin password: ")
else:
    password = os.environ.get('ADMIN_PASSWORD')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Admin created successfully!")
else:
    print(f"Admin '{username}' already exists. Updating...")
    user = User.objects.get(username=username)
    user.email = email
    user.set_password(password)
    user.save()
    print("Admin updated!")

print("\nAll Superusers:")
for user in User.objects.filter(is_superuser=True):
    print(f"  - {user.username} ({user.email})")
