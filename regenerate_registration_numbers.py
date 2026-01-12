"""
Script to regenerate all registration numbers with new random 6-digit format
Run with: python regenerate_registration_numbers.py
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Registration


def regenerate_all_numbers():
    """Regenerate all registration numbers with new random 6-digit format"""
    
    registrations = Registration.objects.all().order_by('created_at')
    
    updated_count = 0
    
    print(f"\nFound {registrations.count()} total registrations\n")
    
    for reg in registrations:
        old_number = reg.registration_number
        
        # Clear the old number temporarily to avoid conflicts
        reg.registration_number = ''
        reg.save(update_fields=['registration_number'])
        
        # Generate new random number
        new_number = Registration.generate_registration_number()
        reg.registration_number = new_number
        reg.save(update_fields=['registration_number'])
        
        updated_count += 1
        print(f"✓ Updated: {reg.name}")
        print(f"  Old: {old_number} → New: {new_number}")
        print(f"  Email: {reg.email}")
        print()
    
    print("=" * 60)
    print(f"✓ Regeneration Complete!")
    print(f"  Updated: {updated_count} registration numbers")
    print("=" * 60)
    
    # Display sample of new registrations
    print("\nSample New Registration Numbers:")
    print("-" * 60)
    for reg in Registration.objects.all()[:5]:
        print(f"  {reg.registration_number} | {reg.name}")
        print(f"  Email: {reg.email}")
        print()


if __name__ == '__main__':
    print("=" * 60)
    print("Regenerating Registration Numbers")
    print("=" * 60)
    print("\nThis will regenerate ALL registration numbers with")
    print("new random 6-digit format (ON26-XXXXXX)")
    print()
    
    confirm = input("Continue? (yes/no): ").strip().lower()
    if confirm in ('yes', 'y'):
        regenerate_all_numbers()
    else:
        print("\nCancelled. No changes made.")
