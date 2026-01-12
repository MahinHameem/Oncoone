#!/usr/bin/env python
"""
DANGER: Clear ALL data from production database EXCEPT courses
Run this on the server: python clear_production_data.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/var/www/oncoone')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Registration, StudentCourseEnrollment, Payment, PaymentInvoice, PaymentOTP, Course


def clear_all_data_except_courses():
    """Delete all student/payment data but keep courses"""
    
    print("=" * 70)
    print("⚠️  WARNING: PRODUCTION DATABASE CLEANUP")
    print("=" * 70)
    print("\nThis will DELETE:")
    print(f"  - {Registration.objects.count()} Registrations (students)")
    print(f"  - {StudentCourseEnrollment.objects.count()} Course Enrollments")
    print(f"  - {Payment.objects.count()} Payments")
    print(f"  - {PaymentInvoice.objects.count()} Payment Invoices")
    print(f"  - {PaymentOTP.objects.count()} Payment OTPs")
    print("\nThis will KEEP:")
    print(f"  - {Course.objects.count()} Courses ✅")
    print("=" * 70)
    
    # Ask for confirmation
    confirm = input("\n⚠️  Type 'DELETE ALL DATA' to confirm: ")
    
    if confirm != "DELETE ALL DATA":
        print("\n❌ Cancelled. No data was deleted.")
        return
    
    print("\n🗑️  Deleting data...")
    
    # Delete in correct order (respecting foreign keys)
    payment_invoices_count = PaymentInvoice.objects.count()
    PaymentInvoice.objects.all().delete()
    print(f"✓ Deleted {payment_invoices_count} payment invoices")
    
    payment_otps_count = PaymentOTP.objects.count()
    PaymentOTP.objects.all().delete()
    print(f"✓ Deleted {payment_otps_count} payment OTPs")
    
    payments_count = Payment.objects.count()
    Payment.objects.all().delete()
    print(f"✓ Deleted {payments_count} payments")
    
    enrollments_count = StudentCourseEnrollment.objects.count()
    StudentCourseEnrollment.objects.all().delete()
    print(f"✓ Deleted {enrollments_count} course enrollments")
    
    registrations_count = Registration.objects.count()
    Registration.objects.all().delete()
    print(f"✓ Deleted {registrations_count} student registrations")
    
    print("\n" + "=" * 70)
    print("✅ DATABASE CLEANED!")
    print("=" * 70)
    print("\nRemaining data:")
    print(f"  - Courses: {Course.objects.count()} ✅")
    print(f"  - Registrations: {Registration.objects.count()}")
    print(f"  - Enrollments: {StudentCourseEnrollment.objects.count()}")
    print(f"  - Payments: {Payment.objects.count()}")
    print("=" * 70)
    print("\n💡 Your database is now ready for fresh student registrations!")


if __name__ == '__main__':
    clear_all_data_except_courses()
