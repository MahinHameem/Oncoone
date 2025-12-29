import django
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

# Get table info
with connection.cursor() as cursor:
    # PostgreSQL query
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'core_registration'
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()

print("core_registration table columns:")
for col in columns:
    print(f"  {col[0]}: {col[1]} (nullable: {col[2]})")
