# Seed demo payments for student id 3
# - $2000 for first course
# - $300 for second course
# Usage: python seed_demo_payment.py

import os
import sys
from decimal import Decimal

import django
from django.utils import timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append(BASE_DIR)

django.setup()

from core.models import Registration, StudentCourseEnrollment, CoursePrice, Payment  # noqa: E402


def create_payment(student, enrollment, amount):
    """Create a completed payment for the given enrollment"""
    course_price = CoursePrice.objects.filter(course_name=enrollment.course_name).first()
    total_price = course_price.price_cad if course_price else Decimal('0.00')

    payment_amount = Decimal(str(amount))
    tax_amount = (payment_amount * Decimal('0.05')).quantize(Decimal('0.01'))
    final_amount = payment_amount + tax_amount

    payment = Payment.objects.create(
        registration=student,
        enrollment=enrollment,
        student_id=str(student.id),
        course_name=enrollment.course_name,
        total_price_cad=total_price,
        payment_amount_cad=payment_amount,
        tax_amount=tax_amount,
        final_amount_cad=final_amount,
        status='completed',
        payment_method='visa',
        card_holder_name='Demo User',
        card_last_four='4242',
        transaction_id=f'DEMO-{timezone.now().strftime("%Y%m%d%H%M%S")}-{enrollment.id}',
    )

    # Generate invoice number
    try:
        payment.generate_invoice_number()
        payment.save()
    except Exception:
        pass

    return payment


def main():
    try:
        student = Registration.objects.get(id=3)
    except Registration.DoesNotExist:
        print('Student with id=3 not found')
        return

    enrollments = list(student.course_enrollments.all())
    if not enrollments:
        print('Student id=3 has no enrollments; cannot seed payments.')
        return

    # Create $2000 payment for first course
    if len(enrollments) >= 1:
        payment1 = create_payment(student, enrollments[0], 2000.00)
        print(f"✓ Seeded payment {payment1.invoice_number} - $2000.00 for {enrollments[0].course_name}")

    # Create $300 payment for second course
    if len(enrollments) >= 2:
        payment2 = create_payment(student, enrollments[1], 300.00)
        print(f"✓ Seeded payment {payment2.invoice_number} - $300.00 for {enrollments[1].course_name}")
    else:
        print(f"⚠ Student only has {len(enrollments)} enrollment(s). Second payment not created.")


if __name__ == '__main__':
    main()
