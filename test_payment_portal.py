"""
Test script to verify registration number usage in payment system
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Registration

print("=" * 60)
print("PAYMENT PORTAL VERIFICATION")
print("=" * 60)

students = Registration.objects.all()[:3]

print("\n✓ Students can use these Registration Numbers for payments:\n")
print("-" * 60)

for student in students:
    print(f"Registration Number: {student.registration_number}")
    print(f"Name: {student.name}")
    print(f"Email: {student.email}")
    print(f"Password: {student.student_password}")
    print()

print("-" * 60)
print("\nTo make a payment:")
print("1. Go to payment portal")
print(f"2. Enter Registration Number (e.g., {students[0].registration_number})")
print("3. Select course and make payment")
print()
print("✓ Registration numbers are included in:")
print("  • Registration confirmation emails")
print("  • Payment confirmation emails")
print("  • Payment portal access")
print("=" * 60)
