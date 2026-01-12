"""
Script to update existing registrations with new registration numbers and passwords
Run with: python update_existing_registrations.py
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Registration


def update_registrations():
    """Update existing registrations with registration numbers and passwords"""
    
    registrations = Registration.objects.all().order_by('created_at')
    
    updated_count = 0
    skipped_count = 0
    
    print(f"\nFound {registrations.count()} total registrations\n")
    
    for reg in registrations:
        needs_update = False
        changes = []
        
        # Check if registration_number needs to be set
        if not reg.registration_number or reg.registration_number == 'ON26-0000':
            old_number = reg.registration_number
            reg.registration_number = Registration.generate_registration_number()
            changes.append(f"Registration Number: {old_number or 'None'} → {reg.registration_number}")
            needs_update = True
        
        # Check if student_password needs to be set
        if not reg.student_password:
            reg.student_password = reg.generate_unique_password()
            changes.append(f"Password: Generated ({reg.student_password})")
            needs_update = True
        
        if needs_update:
            reg.save()
            updated_count += 1
            print(f"✓ Updated: {reg.name} ({reg.email})")
            for change in changes:
                print(f"  - {change}")
            print()
        else:
            skipped_count += 1
    
    print("=" * 60)
    print(f"Update Complete!")
    print(f"  Updated: {updated_count} registrations")
    print(f"  Skipped: {skipped_count} registrations (already have values)")
    print(f"  Total: {registrations.count()} registrations")
    print("=" * 60)
    
    # Display sample of registrations
    print("\nSample Registrations:")
    print("-" * 60)
    for reg in Registration.objects.all()[:5]:
        print(f"  {reg.registration_number} | {reg.name}")
        print(f"  Email: {reg.email}")
        print(f"  Password: {reg.student_password}")
        print()


if __name__ == '__main__':
    print("=" * 60)
    print("Updating Existing Registrations")
    print("=" * 60)
    print("\nThis script will:")
    print("  1. Generate registration numbers for students without them")
    print("  2. Generate unique passwords for students without them")
    print()
    
    confirm = input("Continue? (yes/no): ").strip().lower()
    if confirm in ('yes', 'y'):
        update_registrations()
    else:
        print("\nCancelled. No changes made.")
