import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

# Reset the migration state
with connection.cursor() as cursor:
    try:
        cursor.execute("DELETE FROM django_migrations WHERE app = 'core' AND name = '0004_add_registration_fields';")
        print("Deleted migration record for 0004_add_registration_fields")
    except Exception as e:
        print(f"Error: {e}")

print("Done!")
