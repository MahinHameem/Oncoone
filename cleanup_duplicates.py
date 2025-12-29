import django
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

# Get duplicate emails directly from the database
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT email, COUNT(*) as count 
        FROM core_registration 
        GROUP BY email 
        HAVING COUNT(*) > 1
    """)
    duplicates = cursor.fetchall()

print(f"Found {len(duplicates)} duplicate emails:\n")

for email, count in duplicates:
    with connection.cursor() as cursor:
        # Get all registrations with this email, ordered by id (oldest first)
        cursor.execute("""
            SELECT id, name, created_at 
            FROM core_registration 
            WHERE email = %s
            ORDER BY created_at ASC
        """, [email])
        regs = cursor.fetchall()
    
    print(f"Email: {email} ({count} registrations)")
    
    # Keep the oldest, delete newer ones
    keep_id = regs[0][0]
    keep_name = regs[0][1]
    print(f"  - Keeping ID {keep_id}: {keep_name}")
    
    for reg_id, reg_name, created_at in regs[1:]:
        print(f"  - Deleting ID {reg_id}: {reg_name} (created {created_at})")
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM core_registration WHERE id = %s", [reg_id])

print("\nDuplicate removal complete!")


