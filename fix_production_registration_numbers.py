#!/usr/bin/env python
"""
Fix production database - populate empty registration numbers
Run this on the server BEFORE running migrations
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/var/www/oncoone')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Registration

def fix_registration_numbers():
    """Populate all empty registration numbers"""
    
    # Find all registrations with empty or null registration numbers
    empty_regs = Registration.objects.filter(
        registration_number__in=['', None]
    ) | Registration.objects.filter(
        registration_number__isnull=True
    )
    
    count = empty_regs.count()
    print(f"Found {count} registrations without registration numbers")
    
    if count == 0:
        print("✅ All registrations already have numbers!")
        return
    
    # Generate unique registration numbers for each
    updated = 0
    for reg in empty_regs:
        # This will auto-generate on save
        reg.registration_number = None  # Reset to trigger generation
        reg.save()
        print(f"✓ Generated: {reg.name} → {reg.registration_number}")
        updated += 1
    
    print(f"\n✅ Updated {updated} registration numbers!")
    print("Now you can safely run: python manage.py migrate")

if __name__ == '__main__':
    fix_registration_numbers()
