import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Registration

reg = Registration.objects.first()
if reg:
    print(f"Registration ID (property): {reg.registration_id}")
    print(f"Name: {reg.name}")
    print(f"Email: {reg.email}")
else:
    print("No registrations found")
