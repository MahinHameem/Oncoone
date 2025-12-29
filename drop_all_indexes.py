import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

# Drop all problematic indexes
with connection.cursor() as cursor:
    # List all indexes on the registration_id column
    cursor.execute("""
        SELECT indexname
        FROM pg_indexes
        WHERE tablename = 'core_registration' AND indexdef LIKE '%registration_id%'
    """)
    indexes = cursor.fetchall()
    print(f"Found {len(indexes)} indexes on registration_id:")
    for (index_name,) in indexes:
        print(f"  - {index_name}")
        try:
            cursor.execute(f"DROP INDEX IF EXISTS {index_name};")
            print(f"    Dropped: {index_name}")
        except Exception as e:
            print(f"    Error: {e}")

print("Cleanup complete!")
