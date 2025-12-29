import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

# Drop problematic indexes and column
with connection.cursor() as cursor:
    try:
        cursor.execute("DROP INDEX IF EXISTS core_registration_registration_id_1d503a36_like;")
        print("Dropped index: core_registration_registration_id_1d503a36_like")
    except Exception as e:
        print(f"Could not drop index: {e}")
    
    try:
        cursor.execute("ALTER TABLE core_registration DROP COLUMN IF EXISTS registration_id;")
        print("Dropped column: registration_id")
    except Exception as e:
        print(f"Could not drop column: {e}")
    
    try:
        cursor.execute("ALTER TABLE core_registration DROP COLUMN IF EXISTS password_hash;")
        print("Dropped column: password_hash")
    except Exception as e:
        print(f"Could not drop column: {e}")
    
    try:
        cursor.execute("ALTER TABLE core_registration DROP COLUMN IF EXISTS updated_at;")
        print("Dropped column: updated_at")
    except Exception as e:
        print(f"Could not drop column: {e}")

print("Cleanup complete!")

