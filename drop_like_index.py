import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

# Drop the problematic like index
with connection.cursor() as cursor:
    try:
        cursor.execute("DROP INDEX IF EXISTS core_registration_registration_id_1d503a36_like CASCADE;")
        print("Dropped index: core_registration_registration_id_1d503a36_like")
    except Exception as e:
        print(f"Error dropping index: {e}")
    
    # List all indexes on core_registration
    cursor.execute("""
        SELECT indexname
        FROM pg_indexes
        WHERE tablename = 'core_registration'
        ORDER BY indexname
    """)
    indexes = cursor.fetchall()
    print(f"\nRemaining indexes on core_registration:")
    for (index_name,) in indexes:
        print(f"  - {index_name}")

print("\nDone!")
