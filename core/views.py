from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import EmailMessage
from django.core.files.base import ContentFile
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum
import json
import uuid
import logging

from .models import Registration, StudentCourseEnrollment, Payment, CoursePrice, PaymentInvoice, PaymentOTP
from .stripe_processor import StripePaymentProcessor
from .payment_security import OTPSecurityManager, PaymentSecurityValidator

# Initialize loggers
logger = logging.getLogger('core.payment')
security_logger = logging.getLogger('core.security')


@csrf_exempt
def register_view(request):
    """Handle course registration - supports multiple courses per student"""
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)

    try:
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        contact = request.POST.get('contact', '').strip()
        course_name = request.POST.get('course', '').strip() or 'Course'
        has_prerequisite = request.POST.get('hasQualification', 'yes').lower() in ('yes', '1', 'true')
        proof = request.FILES.get('proof')

        if not (name and email and contact):
            return HttpResponseBadRequest('Missing required fields')

        # Validate prerequisite requirement
        if has_prerequisite and not proof:
            return HttpResponseBadRequest('Proof of prerequisite is required')

        # Process file upload
        proof_bytes = None
        proof_name = None
        proof_mime = None
        if proof:
            allowed_mimes = ('image/png', 'image/jpeg', 'image/jpg', 'application/pdf')
            max_size = 5 * 1024 * 1024  # 5 MB
            proof_name = proof.name
            proof_mime = getattr(proof, 'content_type', None)
            if proof_mime and proof_mime.lower() not in allowed_mimes:
                return HttpResponseBadRequest('Unsupported file type')
            if hasattr(proof, 'size') and proof.size and proof.size > max_size:
                return HttpResponseBadRequest('File too large (max 5MB)')
            try:
                proof_bytes = proof.read()
                try:
                    proof.seek(0)
                except Exception:
                    pass
            except Exception:
                proof_bytes = None

        # Get or create registration for this email
        reg, created = Registration.objects.get_or_create(
            email=email,
            defaults={
                'name': name,
                'contact': contact,
            }
        )

        # Check if already enrolled in this course
        if StudentCourseEnrollment.objects.filter(registration=reg, course_name=course_name).exists():
            return JsonResponse({
                'status': 'error',
                'error': f'You are already registered for {course_name}. Please choose a different course or contact support.'
            }, status=400)

        # Create course enrollment
        enrollment = StudentCourseEnrollment.objects.create(
            registration=reg,
            course_name=course_name,
            has_prerequisite=has_prerequisite,
            proof=proof if proof else None,
            proof_name=proof_name,
            proof_mime=proof_mime,
            proof_data=proof_bytes,
        )

        # Send admin notification
        admin_email = getattr(settings, 'ADMIN_EMAIL', '')
        if admin_email:
            try:
                subject = f'New course enrollment: {reg.name} for {course_name}'
                body = (
                    f"Student Name: {reg.name}\n"
                    f"Email: {reg.email}\n"
                    f"Contact: {reg.contact}\n"
                    f"Course: {course_name}\n"
                    f"Has Prerequisite: {has_prerequisite}\n"
                    f"Registration ID: {reg.registration_id}\n"
                    f"Submitted: {enrollment.enrolled_at}\n"
                )
                email_msg = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [admin_email])
                if proof:
                    proof.seek(0)
                    email_msg.attach(proof_name, proof.read(), proof_mime)
                email_msg.send(fail_silently=True)
            except Exception as exc:
                print(f"Admin email failed: {exc}")

        # Send confirmation to student
        if reg.email:
            try:
                user_subject = f"Welcome to OncoOne - Registration ID: {reg.registration_id}"
                user_body = (
                    f"Hi {reg.name},\n\n"
                    f"Thank you for registering for {course_name}!\n\n"
                    f"Your Registration ID: {reg.registration_id}\n"
                    f"Email: {reg.email}\n\n"
                    f"You can use this ID to access the payment portal.\n\n"
                    f"– OncoOne Team"
                )
                EmailMessage(user_subject, user_body, settings.DEFAULT_FROM_EMAIL, [reg.email]).send(fail_silently=True)
            except Exception:
                pass

        return JsonResponse({
            'status': 'ok',
            'id': reg.id,
            'registration_id': reg.registration_id,
            'enrollment_id': enrollment.id,
            'message': f'Registration for {course_name} successful! Your Registration ID is: {reg.registration_id}'
        })

    except Exception as e:
        print(f"Registration error: {e}")
        return JsonResponse({'status': 'error', 'error': str(e)}, status=500)


# Admin API: list, edit, delete registrations (development use only)
@csrf_exempt
def registrations_list(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    regs = Registration.objects.order_by('-created_at').all()
    data = []
    for r in regs:
        # Get all course enrollments for this student
        enrollments = r.course_enrollments.all()
        courses = [e.course_name for e in enrollments]
        course_total = Decimal('0.00')
        for e in enrollments:
            course_price = CoursePrice.objects.filter(course_name=e.course_name).first()
            price = course_price.price_cad if course_price else None
            if price is None:
                paid_course = e.payments.filter(status='completed').first()
                price = paid_course.total_price_cad if paid_course else Decimal('0.00')
            course_total += price

        completed_payments = r.payments.filter(status='completed')
        total_paid = sum((p.payment_amount_cad for p in completed_payments), Decimal('0.00'))
        balance_raw = course_total - total_paid
        balance = balance_raw if balance_raw > Decimal('0.00') else Decimal('0.00')

        if course_total == Decimal('0.00') and total_paid == Decimal('0.00'):
            payment_status = 'pending'
        else:
            payment_status = 'completed' if balance_raw <= Decimal('0.00') else 'pending'

        data.append({
            'id': r.id,
            'name': r.name,
            'email': r.email,
            'contact': r.contact,
            'courses': courses,
            'course_display': ', '.join(courses) if courses else 'N/A',
            'course_count': len(courses),
            'course_total_cad': f"{course_total.quantize(Decimal('0.01'))}",
            'total_paid_cad': f"{total_paid.quantize(Decimal('0.01'))}",
            'balance_cad': f"{balance.quantize(Decimal('0.01'))}",
            'payment_status': payment_status,
            'created_at': r.created_at.isoformat(),
        })
    return JsonResponse({'results': data})


@csrf_exempt
def registration_detail(request, pk):
    reg = get_object_or_404(Registration, pk=pk)

    if request.method == 'GET':
        # Get all course enrollments
        enrollments = reg.course_enrollments.all()
        enrollments_data = [
            {
                'id': e.id,
                'course_name': e.course_name,
                'has_prerequisite': e.has_prerequisite,
                'enrollment_status': e.enrollment_status,
                'enrolled_at': e.enrolled_at.isoformat(),
            }
            for e in enrollments
        ]
        
        return JsonResponse({
            'id': reg.id,
            'name': reg.name,
            'email': reg.email,
            'contact': reg.contact,
            'enrollments': enrollments_data,
            'created_at': reg.created_at.isoformat(),
        })

    if request.method in ('PUT', 'PATCH'):
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except Exception:
            return HttpResponseBadRequest('Invalid JSON')

        changed = False
        for field in ('name', 'email', 'contact'):
            if field in payload:
                setattr(reg, field, payload[field])
                changed = True
        if changed:
            reg.save()
        return JsonResponse({'status': 'ok'})

    if request.method == 'DELETE':
        reg.delete()
        return JsonResponse({'status': 'deleted'})

    return HttpResponseNotAllowed(['GET', 'PUT', 'PATCH', 'DELETE'])


@staff_member_required
def download_proof_db(request, pk):
    enrollment = get_object_or_404(StudentCourseEnrollment, pk=pk)
    if not enrollment.proof_data:
        return HttpResponse(status=404)
    # stream DB bytes as attachment
    resp = HttpResponse(enrollment.proof_data, content_type=enrollment.proof_mime or 'application/octet-stream')
    filename = enrollment.proof_name or f'enrollment-{enrollment.id}-proof'
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp


@staff_member_required
def download_proof(request, pk):
    """Serve attached proof whether stored in DB (`proof_data`) or on disk (`proof`)."""
    enrollment = get_object_or_404(StudentCourseEnrollment, pk=pk)
    # Prefer DB-stored bytes
    if enrollment.proof_data:
        resp = HttpResponse(enrollment.proof_data, content_type=enrollment.proof_mime or 'application/octet-stream')
        filename = enrollment.proof_name or f'enrollment-{enrollment.id}-proof'
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        return resp

    # Fallback to FileField on-disk file
    if enrollment.proof:
        try:
            # use FileResponse for efficient file streaming
            from django.http import FileResponse
            enrollment.proof.open('rb')
            filename = enrollment.proof.name.split('/')[-1]
            response = FileResponse(enrollment.proof, as_attachment=True, filename=filename)
            return response
        except Exception:
            return HttpResponse(status=500)

    return HttpResponse(status=404)


@staff_member_required
def admin_students_page(request):
    """Render the admin students page (served from Django so admin session authenticates downloads)."""
    return render(request, 'admin/students.html')


@staff_member_required
def admin_courses_page(request):
    """Render the admin courses editor page."""
    return render(request, 'admin/courses-admin.html')


@staff_member_required
def admin_payments_page(request):
    """Render the admin payments page."""
    return render(request, 'admin/payments.html')


@staff_member_required
def admin_payments_list(request):
    """API endpoint to get all payments with student details."""

    try:
        payments = Payment.objects.select_related('registration').all().order_by('-created_at')

        payments_data = []
        for payment in payments:
            # Sum all completed payments for the same student and course to show an accurate balance
            paid_agg = Payment.objects.filter(
                registration=payment.registration,
                course_name=payment.course_name,
                status='completed'
            ).aggregate(paid=Sum('payment_amount_cad'))

            paid_sum = Decimal(paid_agg.get('paid') or 0).quantize(Decimal('0.01'))
            full_price = Decimal(payment.total_price_cad).quantize(Decimal('0.01'))
            remaining = (full_price - paid_sum)
            remaining = remaining if remaining > Decimal('0.00') else Decimal('0.00')

            payments_data.append({
                'id': payment.id,
                'invoice_number': payment.invoice_number,
                'student_name': payment.registration.name,
                'student_email': payment.registration.email,
                'course_name': payment.course_name,
                'payment_amount_cad': str(payment.payment_amount_cad),
                'total_price_cad': str(payment.total_price_cad),
                'tax_amount': str(payment.tax_amount),
                'final_amount_cad': str(payment.final_amount_cad),
                'status': payment.status,
                'payment_method': payment.payment_method or 'N/A',
                'created_at': payment.created_at.isoformat(),
                'completed_at': payment.completed_at.isoformat() if payment.completed_at else None,
                'paid_total_cad': str(paid_sum),
                'remaining_cad': str(remaining),
            })

        return JsonResponse({
            'status': 'success',
            'payments': payments_data,
            'total': len(payments_data)
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)


@staff_member_required
def admin_download_invoice(request, payment_id):
    """Download invoice PDF for a payment."""
    try:
        payment = Payment.objects.get(id=payment_id)
        
        # Check if payment has invoice
        if not hasattr(payment, 'invoice') or not payment.invoice.invoice_pdf:
            # Generate invoice if it doesn't exist
            if payment.status == 'completed':
                if not payment.invoice_number:
                    payment.generate_invoice_number()
                    payment.save()
                
                invoice, _created = PaymentInvoice.objects.get_or_create(payment=payment)
                pdf_bytes = generate_invoice_pdf(payment)
                pdf_filename = f"invoice_{payment.invoice_number}.pdf"
                invoice.invoice_pdf.save(pdf_filename, ContentFile(pdf_bytes), save=False)
                invoice.save()
            else:
                return HttpResponse('Invoice can only be generated for completed payments', status=400)
        
        # Serve the PDF
        invoice = payment.invoice
        response = HttpResponse(invoice.invoice_pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{payment.invoice_number}.pdf"'
        return response
        
    except Payment.DoesNotExist:
        return HttpResponse('Payment not found', status=404)
    except Exception as e:
        return HttpResponse(f'Error generating invoice: {str(e)}', status=500)


def staff_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin-students-page')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            auth_login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or None
            return redirect(next_url or 'admin-students-page')
        error = 'Invalid credentials or not authorized.'

    return render(request, 'admin/login.html', {'error': error})


def staff_logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect('staff-login')


# ============== PAYMENT GATEWAY VIEWS ==============

def payment_portal_home(request):
    """Main payment portal page - ask for student ID or registration ID"""
    return render(request, 'payments/payment_portal_home.html')


@csrf_exempt
def payment_verify_student(request):
    """Verify student by ID, Registration ID, or Email and get their registered courses"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        student_id = data.get('student_id', '').strip()
        
        if not student_id:
            return JsonResponse({'error': 'Student ID or Registration ID is required'}, status=400)
        
        # Try multiple search methods
        registration = None
        
        # Try by Registration ID format (REG-YYYYMMDD-XXXXXX)
        if student_id.startswith('REG-'):
            try:
                # Extract numeric ID from REG-20251229-000073 format
                parts = student_id.split('-')
                if len(parts) == 3:
                    numeric_id = int(parts[2])  # Get the last part (000073)
                    registration = Registration.objects.filter(id=numeric_id).first()
            except (ValueError, IndexError):
                pass
        
        # Try by numeric ID
        if not registration:
            try:
                student_id_int = int(student_id)
                registration = Registration.objects.get(id=student_id_int)
            except (ValueError, Registration.DoesNotExist):
                pass
        
        # Try by email
        if not registration:
            registration = Registration.objects.filter(email=student_id).first()
        
        if not registration:
            return JsonResponse({'error': 'Student not found. Please check your Registration ID or email.'}, status=404)
        
        # Get all course enrollments for this student
        enrollments = registration.course_enrollments.all()
        
        # Get course prices for each enrollment
        course_data = []
        for enrollment in enrollments:
            course_price = CoursePrice.objects.filter(course_name=enrollment.course_name).first()
            if course_price:
                course_data.append({
                    'id': course_price.id,
                    'enrollment_id': enrollment.id,
                    'name': enrollment.course_name,
                    'price': str(course_price.price_cad),
                    'description': course_price.description or '',
                    'status': enrollment.enrollment_status
                })
            else:
                # If no price set, show placeholder
                course_data.append({
                    'id': None,
                    'enrollment_id': enrollment.id,
                    'name': enrollment.course_name,
                    'price': '0.00',
                    'description': 'Price not set',
                    'status': enrollment.enrollment_status
                })
        
        return JsonResponse({
            'status': 'ok',
            'student': {
                'id': registration.id,
                'name': registration.name,
                'email': registration.email,
                'contact': registration.contact,
            },
            'courses': course_data,
            'course_count': len(course_data)
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def payment_select_course(request, student_id):
    """Page to select course and enter payment amount"""
    try:
        student_id_int = int(student_id)
        registration = Registration.objects.get(id=student_id_int)
    except (ValueError, Registration.DoesNotExist):
        return redirect('payment-portal-home')
    
    # Get all course enrollments
    enrollments = registration.course_enrollments.all()
    if not enrollments.exists():
        # No enrollments found
        return render(request, 'payments/payment_select_amount.html', {
            'student': registration,
            'enrollments': [],
            'error': 'No course enrollments found. Please register first.'
        })
    
    # Build course data for template
    from django.db.models import Sum
    course_data = []
    for enrollment in enrollments:
        course_price = CoursePrice.objects.filter(course_name=enrollment.course_name).first()
        full_price = float(course_price.price_cad) if course_price else 0.00
        
        # Calculate already paid for this enrollment
        paid_sum = Payment.objects.filter(enrollment=enrollment, status='completed').aggregate(
            paid=Sum('payment_amount_cad')
        )['paid'] or 0
        paid_sum = float(paid_sum)
        remaining = max(full_price - paid_sum, 0.0)
        
        course_data.append({
            'enrollment_id': enrollment.id,
            'course_name': enrollment.course_name,
            'price': full_price,
            'paid_so_far': paid_sum,
            'remaining': remaining,
            'is_fully_paid': remaining <= 0.01,
            'description': course_price.description if course_price else 'Price not set'
        })
    
    context = {
        'student': registration,
        'enrollments': enrollments,
        'courses': course_data,
        'currency': 'CAD'
    }
    
    return render(request, 'payments/payment_select_amount.html', context)


def payment_amount(request, student_id):
    """Page to enter payment amount for a selected course"""
    try:
        student_id_int = int(student_id)
        registration = Registration.objects.get(id=student_id_int)
    except (ValueError, Registration.DoesNotExist):
        return redirect('payment-portal-home')
    
    # Get enrollment_id from query params
    enrollment_id = request.GET.get('enrollment_id')
    if not enrollment_id:
        return redirect('payment-select-course', student_id=student_id)
    
    try:
        enrollment = StudentCourseEnrollment.objects.get(id=int(enrollment_id), registration=registration)
    except (ValueError, StudentCourseEnrollment.DoesNotExist):
        return redirect('payment-portal-home')
    
    # Get course price
    course_price = CoursePrice.objects.filter(course_name=enrollment.course_name).first()
    full_price = float(course_price.price_cad) if course_price else 0.00

    # Sum of previous completed payments for this enrollment (amount before tax)
    from django.db.models import Sum
    paid_sum = Payment.objects.filter(enrollment=enrollment, status='completed').aggregate(
        paid=Sum('payment_amount_cad')
    )['paid'] or 0
    paid_sum = float(paid_sum)

    remaining_price = max(full_price - paid_sum, 0.0)
    
    # If already fully paid, redirect to success page
    if remaining_price <= 0.01:
        return redirect('payment-already-paid', student_id=student_id, enrollment_id=enrollment_id)
    
    context = {
        'student': registration,
        'enrollment': enrollment,
        'course_name': enrollment.course_name,
        'total_price': remaining_price,
        'course_full_price': full_price,
        'paid_so_far': paid_sum,
        'enrollment_id': enrollment_id,
        'currency': 'CAD'
    }
    
    return render(request, 'payments/payment_amount.html', context)


def payment_already_paid(request, student_id, enrollment_id):
    """Show success message when course is already fully paid"""
    try:
        student_id_int = int(student_id)
        registration = Registration.objects.get(id=student_id_int)
        enrollment = StudentCourseEnrollment.objects.get(id=enrollment_id, registration=registration)
    except (ValueError, Registration.DoesNotExist, StudentCourseEnrollment.DoesNotExist):
        return redirect('payment-portal-home')
    
    context = {
        'student': registration,
        'enrollment': enrollment,
        'course_name': enrollment.course_name,
        'registration_id': registration.registration_id,
    }
    
    return render(request, 'payments/payment_already_paid.html', context)


@csrf_exempt
def payment_calculate_tax(request):
    """Calculate tax for the payment"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        payment_amount = Decimal(str(data.get('amount', '0')))
        
        # Canadian tax (GST/HST) - simplified at 5% (adjust based on province)
        tax_rate = Decimal('0.05')  # 5% tax
        tax_amount = (payment_amount * tax_rate).quantize(Decimal('0.01'))
        total_amount = payment_amount + tax_amount
        
        return JsonResponse({
            'status': 'ok',
            'payment_amount': str(payment_amount),
            'tax_amount': str(tax_amount),
            'total_amount': str(total_amount),
            'currency': 'CAD'
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def payment_summary(request, student_id):
    """Payment summary page before card entry"""
    try:
        student_id_int = int(student_id)
        registration = Registration.objects.get(id=student_id_int)
    except (ValueError, Registration.DoesNotExist):
        return redirect('payment-portal-home')
    
    # Get enrollment_id from query params
    enrollment_id = request.GET.get('enrollment_id')
    enrollment = None
    if enrollment_id:
        try:
            enrollment = StudentCourseEnrollment.objects.get(id=int(enrollment_id), registration=registration)
        except (ValueError, StudentCourseEnrollment.DoesNotExist):
            return redirect('payment-portal-home')
    else:
        # Default to first enrollment if not specified
        enrollment = registration.course_enrollments.first()
        if not enrollment:
            return redirect('payment-portal-home')
    
    # Get values from session or query params
    payment_amount = request.GET.get('amount', '0')
    tax_amount = request.GET.get('tax', '0')
    total_amount = request.GET.get('total', '0')
    
    course_price = CoursePrice.objects.filter(course_name=enrollment.course_name).first()
    course_full_price = float(course_price.price_cad) if course_price else 0.00

    # Include previously paid amounts so summary shows true remaining
    from django.db.models import Sum
    paid_sum = Payment.objects.filter(enrollment=enrollment, status='completed').aggregate(
        paid=Sum('payment_amount_cad')
    )['paid'] or 0
    paid_sum = float(paid_sum)
    remaining_balance = max(course_full_price - (paid_sum + float(payment_amount)), 0.0)
    
    context = {
        'student': registration,
        'student_id': registration.id,
        'enrollment': enrollment,
        'course': enrollment.course_name,
        'payment_amount': float(payment_amount),
        'tax_amount': float(tax_amount),
        'total_amount': float(total_amount),
        'course_full_price': course_full_price,
        'paid_so_far': paid_sum,
        'remaining_balance': max(remaining_balance, 0),
        'currency': 'CAD'
    }
    
    return render(request, 'payments/payment_summary.html', context)


def payment_card_entry(request, student_id):
    """Card entry page with Stripe integration"""
    try:
        student_id_int = int(student_id)
        registration = Registration.objects.get(id=student_id_int)
    except (ValueError, Registration.DoesNotExist):
        return redirect('payment-portal-home')
    
    # Get enrollment_id from query params
    enrollment_id = request.GET.get('enrollment_id')
    enrollment = None
    if enrollment_id:
        try:
            enrollment = StudentCourseEnrollment.objects.get(id=int(enrollment_id))
            if enrollment.registration != registration:
                return redirect('payment-portal-home')
        except (ValueError, StudentCourseEnrollment.DoesNotExist):
            return redirect('payment-portal-home')
    else:
        # If no enrollment specified, get the first one
        enrollment = registration.course_enrollments.first()
        if not enrollment:
            return redirect('payment-portal-home')
    
    # Get course price
    course_price = CoursePrice.objects.filter(course_name=enrollment.course_name).first()
    price = course_price.price_cad if course_price else Decimal('0.00')
    
    payment_amount = request.GET.get('amount', str(price))
    tax_amount = request.GET.get('tax', '0')
    total_amount = request.GET.get('total', payment_amount)
    
    context = {
        'student': registration,
        'student_id': registration.id,
        'student_email': registration.email,
        'enrollment': enrollment,
        'enrollment_id': enrollment.id,
        'course': enrollment.course_name,
        'payment_amount': float(payment_amount),
        'tax_amount': float(tax_amount),
        'total_amount': float(total_amount),
        'currency': 'CAD',
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    }
    
    return render(request, 'payments/payment_card_form_stripe.html', context)


@csrf_exempt
def process_payment(request):
    """Process card payment - simulated for demo"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        
        student_id = data.get('student_id')
        enrollment_id = data.get('enrollment_id')
        payment_amount = Decimal(str(data.get('payment_amount', '0')))
        tax_amount = Decimal(str(data.get('tax_amount', '0')))
        total_amount = Decimal(str(data.get('total_amount', '0')))
        card_holder = data.get('card_holder', '').strip()
        card_type = data.get('card_type', '').lower()
        card_number = data.get('card_number', '').replace(' ', '')
        expiry_month = data.get('expiry_month', '')
        expiry_year = data.get('expiry_year', '')
        cvn = data.get('cvn', '')
        terms_agreed = data.get('terms_agreed', False)
        
        # Validation
        if not all([student_id, card_holder, card_type, card_number, expiry_month, expiry_year, cvn]):
            return JsonResponse({'error': 'Missing required payment information'}, status=400)
        
        if not terms_agreed:
            return JsonResponse({'error': 'You must agree to terms and conditions'}, status=400)
        
        if card_type not in ['visa', 'mastercard']:
            return JsonResponse({'error': 'Invalid card type'}, status=400)
        
        # Validate card number (basic check)
        if not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19:
            return JsonResponse({'error': 'Invalid card number'}, status=400)
        
        # Get registration
        try:
            student_id_int = int(student_id)
            registration = Registration.objects.get(id=student_id_int)
        except (ValueError, Registration.DoesNotExist):
            return JsonResponse({'error': 'Student not found'}, status=404)
        
        # Get enrollment
        enrollment = None
        if enrollment_id:
            try:
                enrollment = StudentCourseEnrollment.objects.get(id=int(enrollment_id))
                if enrollment.registration != registration:
                    return JsonResponse({'error': 'Invalid enrollment'}, status=400)
            except (ValueError, StudentCourseEnrollment.DoesNotExist):
                return JsonResponse({'error': 'Enrollment not found'}, status=404)
        else:
            # Get first enrollment if not specified
            enrollment = registration.course_enrollments.first()
        
        if not enrollment:
            return JsonResponse({'error': 'No course enrollment found'}, status=404)
        
        # Extract last 4 digits of card
        card_last_four = card_number[-4:] if len(card_number) >= 4 else card_number
        
        # Get course price
        course_price_obj = CoursePrice.objects.filter(course_name=enrollment.course_name).first()
        total_price = course_price_obj.price_cad if course_price_obj else Decimal('0.00')
        
        # Create payment record
        payment = Payment.objects.create(
            registration=registration,
            enrollment=enrollment,
            student_id=registration.registration_id,
            course_name=enrollment.course_name,
            total_price_cad=total_price,
            payment_amount_cad=payment_amount,
            tax_amount=tax_amount,
            final_amount_cad=total_amount,
            status='completed',
            payment_method=card_type,
            card_holder_name=card_holder,
            card_last_four=card_last_four,
            transaction_id=str(uuid.uuid4()),
            completed_at=timezone.now()
        )
        
        # Generate invoice number
        payment.generate_invoice_number()
        payment.save()
        
        # Create invoice record
        invoice_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .invoice-header {{ text-align: center; margin-bottom: 30px; }}
                .invoice-title {{ font-size: 28px; font-weight: bold; }}
                .invoice-details {{ margin: 20px 0; }}
                .detail-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #ddd; }}
                .total-row {{ display: flex; justify-content: space-between; padding: 12px 0; font-weight: bold; font-size: 18px; background-color: #f0f0f0; }}
                .label {{ font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="invoice-header">
                <div class="invoice-title">Payment Invoice</div>
                <div>OncoOne Online Payments Portal</div>
            </div>
            
            <div class="invoice-details">
                <div class="detail-row">
                    <span class="label">Invoice Number:</span>
                    <span>{payment.invoice_number}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Date:</span>
                    <span>{payment.completed_at.strftime('%Y-%m-%d %H:%M:%S')}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Student ID:</span>
                    <span>{registration.id}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Student Name:</span>
                    <span>{registration.name}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Email:</span>
                    <span>{registration.email}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Course:</span>
                    <span>{enrollment.course_name}</span>
                </div>
            </div>
            
            <h3>Payment Details</h3>
            <div class="invoice-details">
                <div class="detail-row">
                    <span class="label">Course Fee (CAD):</span>
                    <span>${payment.total_price_cad}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Payment Amount (CAD):</span>
                    <span>${payment.payment_amount_cad}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Tax (5% - GST):</span>
                    <span>${payment.tax_amount}</span>
                </div>
                <div class="total-row">
                    <span>Total Paid (CAD):</span>
                    <span>${payment.final_amount_cad}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Remaining Balance (CAD):</span>
                    <span>${payment.calculate_remaining_balance()}</span>
                </div>
            </div>
            
            <h3>Payment Method</h3>
            <div class="invoice-details">
                <div class="detail-row">
                    <span class="label">Card Type:</span>
                    <span>{card_type.upper()}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Card (Last 4):</span>
                    <span>****{card_last_four}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Cardholder:</span>
                    <span>{card_holder}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Transaction ID:</span>
                    <span>{payment.transaction_id}</span>
                </div>
            </div>
            
            <hr>
            <p style="font-size: 12px; color: #666;">
                Thank you for your payment! This invoice has been generated by OncoOne. 
                For inquiries, please contact support@oncoone.com
            </p>
        </body>
        </html>
        """
        
        PaymentInvoice.objects.create(
            payment=payment,
            invoice_html=invoice_html
        )
        
        # Generate professional PDF invoice
        try:
            invoice_pdf = generate_invoice_pdf(payment)
        except Exception as e:
            print(f"PDF generation failed: {e}")
            invoice_pdf = None
        
        # Send payment confirmation email with PDF attachment
        if registration.email:
            try:
                subject = f"Payment Confirmation - Invoice {payment.invoice_number}"
                body = f"""
Hi {registration.name},

Your payment has been successfully processed!

Invoice Number: {payment.invoice_number}
Student ID: {registration.id}
Registration ID: {registration.registration_id}
Course: {payment.course_name}
Payment Amount: CAD ${payment.payment_amount_cad}
Tax (5% GST): CAD ${payment.tax_amount}
Total Paid: CAD ${payment.final_amount_cad}
Remaining Balance: CAD ${payment.calculate_remaining_balance()}

Card Used (Last 4): {card_last_four}
Transaction ID: {payment.transaction_id}

Your invoice PDF is attached to this email. You can also download it from your student portal using your Registration ID: {registration.registration_id}

Student Portal: {request.build_absolute_uri('/api/payment/')}

Thank you!
– OncoOne Team
                """
                email_msg = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [registration.email])
                
                # Attach PDF if generated successfully
                if invoice_pdf:
                    email_msg.attach(
                        f'Invoice-{payment.invoice_number}.pdf',
                        invoice_pdf,
                        'application/pdf'
                    )
                
                email_msg.send(fail_silently=True)
            except Exception as e:
                print(f"Email send failed: {e}")
        
        return JsonResponse({
            'status': 'success',
            'payment_id': payment.id,
            'invoice_number': payment.invoice_number,
            'transaction_id': payment.transaction_id
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def payment_success(request, payment_id):
    """Payment success page with invoice"""
    try:
        payment = Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        return redirect('payment-portal-home')
    
    remaining_balance = payment.calculate_remaining_balance()
    
    context = {
        'payment': payment,
        'student': payment.registration,
        'remaining_balance': remaining_balance,
        'currency': 'CAD'
    }
    
    return render(request, 'payments/payment_success.html', context)


def payment_cancelled(request, student_id):
    """Payment cancelled page"""
    try:
        student_id_int = int(student_id)
        registration = Registration.objects.get(id=student_id_int)
    except (ValueError, Registration.DoesNotExist):
        return redirect('payment-portal-home')
    
    context = {
        'student': registration
    }
    
    return render(request, 'payments/payment_cancelled.html', context)


# ============== STUDENT PORTAL VIEWS ==============

@csrf_exempt
def student_login(request):
    """Student login page using Student ID or Registration ID"""
    if request.method == 'GET':
        # Return login page
        return render(request, 'payments/student_login.html')
    
    elif request.method == 'POST':
        # Handle JSON login request
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'error': 'Invalid request'}, status=400)
        
        # Extract login credential - single field
        student_input = data.get('student_input', '').strip()
        
        # Validate input is provided
        if not student_input:
            return JsonResponse({
                'status': 'error',
                'error': 'Please enter your Student ID or Registration Number.'
            }, status=400)
        
        # Try to find student by Student ID (numeric) or Registration ID (string)
        student = None
        
        # Try as numeric Student ID first
        try:
            student_id_int = int(student_input)
            student = Registration.objects.filter(id=student_id_int).first()
        except ValueError:
            # Not a number, try as Registration ID
            student = Registration.objects.filter(registration_id=student_input).first()
        
        if student:
            # Store in session
            request.session['student_id'] = student.id
            request.session['student_name'] = student.name
            request.session['registration_id'] = student.registration_id
            
            return JsonResponse({
                'status': 'success',
                'student_id': student.id,
                'student_name': student.name,
                'registration_id': student.registration_id
            })
        else:
            return JsonResponse({
                'status': 'error',
                'error': 'Student not found. Please check your credentials.'
            }, status=404)


def student_logout(request):
    """Student logout"""
    request.session.flush()
    return redirect('student-login')


def payment_invoice_download(request, payment_id):
    """Download invoice PDF for a payment"""
    try:
        payment = Payment.objects.get(id=payment_id)
        student_id = request.session.get('student_id')
        
        # Verify student owns this payment
        if payment.registration.id != student_id:
            return HttpResponse('Unauthorized', status=403)
        
        # Generate PDF invoice
        invoice_pdf = generate_invoice_pdf(payment)
        
        response = HttpResponse(invoice_pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Invoice-{payment.invoice_number}.pdf"'
        return response
    
    except Payment.DoesNotExist:
        return HttpResponse('Payment not found', status=404)
    except Exception as e:
        return HttpResponse(f'Error generating PDF: {str(e)}', status=500)


def generate_invoice_pdf(payment):
    """Generate a minimal PDF invoice for a payment (stable fallback)."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from io import BytesIO

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y = height - 72
    c.setFont("Helvetica-Bold", 18)
    c.drawString(72, y, f"Invoice {payment.invoice_number}")
    y -= 24

    c.setFont("Helvetica", 11)
    lines = [
        f"Student: {payment.registration.name}",
        f"Email: {payment.registration.email}",
        f"Registration ID: {payment.registration.registration_id}",
        f"Course: {payment.course_name}",
        f"Full Course Fee: ${float(payment.total_price_cad):.2f}",
        f"Payment Amount: ${float(payment.payment_amount_cad):.2f}",
        f"Tax: ${float(payment.tax_amount):.2f}",
        f"Total Paid: ${float(payment.final_amount_cad):.2f}",
        f"Status: {payment.get_status_display()}",
    ]
    if getattr(payment, 'created_at', None):
        try:
            lines.append(f"Date: {payment.created_at.strftime('%Y-%m-%d %H:%M')}")
        except Exception:
            pass

    for line in lines:
        c.drawString(72, y, line)
        y -= 16

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


@csrf_exempt
def create_payment_and_send_otp(request):
    """Create payment record with Stripe and send OTP for verification (Production-Ready)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        
        # Extract and sanitize inputs
        student_id = data.get('student_id')
        enrollment_id = data.get('enrollment_id')
        payment_method_id = data.get('payment_method_id')  # Stripe payment method ID
        payment_amount = Decimal(str(data.get('payment_amount', '0')))
        tax_amount = Decimal(str(data.get('tax_amount', '0')))
        total_amount = Decimal(str(data.get('total_amount', '0')))
        card_holder = PaymentSecurityValidator.sanitize_input(data.get('card_holder', ''))
        card_type = data.get('card_type', '').lower().strip()
        card_last_four = data.get('card_last_four', '0000')[:4]
        email = PaymentSecurityValidator.sanitize_input(data.get('email', ''))
        
        # Comprehensive validation
        if not all([student_id, enrollment_id, payment_method_id, card_holder, card_type, email]):
            logger.warning(f'Missing required payment information from {email}')
            return JsonResponse({'error': 'Missing required payment information'}, status=400)
        
        # Validate email format
        if not PaymentSecurityValidator.validate_email_format(email):
            logger.warning(f'Invalid email format: {email}')
            return JsonResponse({'error': 'Invalid email address format'}, status=400)
        
        # Validate card type
        if not PaymentSecurityValidator.validate_card_type(card_type):
            logger.warning(f'Invalid card type: {card_type}')
            return JsonResponse({'error': 'Unsupported card type'}, status=400)
        
        # Validate payment amount
        is_valid, error_msg = PaymentSecurityValidator.validate_payment_amount(total_amount)
        if not is_valid:
            logger.warning(f'Invalid payment amount: ${total_amount} - {error_msg}')
            return JsonResponse({'error': error_msg}, status=400)
        
        # Get registration
        try:
            student_id_int = int(student_id)
            registration = Registration.objects.get(id=student_id_int)
        except (ValueError, Registration.DoesNotExist):
            return JsonResponse({'error': 'Student not found'}, status=404)
        
        # Get enrollment
        try:
            enrollment = StudentCourseEnrollment.objects.get(id=int(enrollment_id), registration=registration)
        except (ValueError, StudentCourseEnrollment.DoesNotExist):
            return JsonResponse({'error': 'Invalid enrollment'}, status=404)
        
        # Get course price
        course_price_obj = CoursePrice.objects.filter(course_name=enrollment.course_name).first()
        if not course_price_obj:
            return JsonResponse({'error': 'Course price not found'}, status=404)
        
        # Create Stripe Payment Intent
        stripe_result = StripePaymentProcessor.create_payment_intent(
            amount_cad=total_amount,
            email=email,
            student_name=registration.name,
            course_name=enrollment.course_name,
            payment_id=None,  # We'll update after creating Payment
            payment_method_id=payment_method_id
        )
        
        if not stripe_result['success']:
            return JsonResponse({'error': f'Payment processing error: {stripe_result["error"]}'}, status=400)
        
        stripe_client_secret = stripe_result['client_secret']
        stripe_payment_intent_id = stripe_result['payment_intent_id']
        
        # Create payment record with 'pending' status (waiting for OTP verification)
        payment = Payment.objects.create(
            registration=registration,
            enrollment=enrollment,
            student_id=str(student_id),
            course_name=enrollment.course_name,
            total_price_cad=course_price_obj.price_cad,
            payment_amount_cad=payment_amount,
            tax_amount=tax_amount,
            final_amount_cad=total_amount,
            status='pending',  # Waiting for OTP verification
            payment_method=card_type,
            card_holder_name=card_holder,
            card_last_four=card_last_four,
            transaction_id=str(uuid.uuid4()),
            stripe_payment_intent_id=stripe_payment_intent_id,
            stripe_customer_id=None  # Will be set after OTP verification
        )
        
        # Create PaymentInvoice record (will be filled after payment confirmation)
        PaymentInvoice.objects.create(payment=payment)
        
        # Create OTP with security settings
        from datetime import timedelta
        otp_expiry_minutes = getattr(settings, 'OTP_EXPIRY_MINUTES', 10)
        
        otp = PaymentOTP.objects.create(
            payment=payment,
            expires_at=timezone.now() + timedelta(minutes=otp_expiry_minutes),
            ip_address=request.META.get('REMOTE_ADDR')
        )
        otp.generate_otp()
        otp.save()
        
        logger.info(f'✅ OTP generated for payment {payment.id} | Student: {email} | Code: {otp.otp_code}')
        
        # Send professional OTP email
        email_sent = False
        try:
            subject = f'🔐 Payment Verification Code - {settings.BUSINESS_NAME}'
            message = f"""
Dear {registration.name},

Thank you for choosing {settings.BUSINESS_NAME}.

To complete your secure payment, please verify your transaction with the following One-Time Password (OTP):

╔═══════════════════════════╗
║   OTP CODE: {otp.otp_code}        ║
╚═══════════════════════════╝

This code is valid for {otp_expiry_minutes} minutes and can be used only once.

📋 PAYMENT SUMMARY
─────────────────────────────────
Course:          {enrollment.course_name}
Payment Amount:  CAD ${payment_amount:.2f}
Tax ({settings.TAX_NAME}):         CAD ${tax_amount:.2f}
Total Amount:    CAD ${total_amount:.2f}
─────────────────────────────────
Payment Method:  {card_type.upper()} ending in {card_last_four}
Cardholder:      {card_holder}

🔒 SECURITY NOTICE:
• Do not share this code with anyone
• Our staff will never ask for your OTP
• You have {settings.OTP_MAX_ATTEMPTS} verification attempts

If you did not initiate this payment, please contact us immediately at {settings.BUSINESS_EMAIL}

Thank you for your trust,
{settings.BUSINESS_NAME} Team
{settings.BUSINESS_EMAIL}
{settings.BUSINESS_PHONE}
            """
            
            email_obj = EmailMessage(
                subject=subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[registration.email],
                reply_to=[settings.BUSINESS_EMAIL]
            )
            email_obj.send(fail_silently=False)
            email_sent = True
            logger.info(f'✅ OTP email sent successfully to {email}')
        except Exception as e:
            logger.error(f'❌ FAILED to send OTP email to {email}: {str(e)} | Type: {type(e).__name__}', exc_info=True)
            # Don't fail the request if email fails
            pass
        
        return JsonResponse({
            'success': True,
            'payment_id': payment.id,
            'stripe_client_secret': stripe_client_secret,
            'email_sent': email_sent,
            'message': f'Payment created. OTP {"sent to " + registration.email if email_sent else "generation failed - please try again."}'
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"Error creating payment: {e}")
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)


@csrf_exempt
def verify_payment_otp(request):
    """Verify OTP for payment with comprehensive security checks (Production-Ready)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        
        payment_id = data.get('payment_id')
        otp_code = data.get('otp_code', '').strip()
        
        # Input validation
        if not all([payment_id, otp_code]):
            security_logger.warning('OTP verification attempted with missing data')
            return JsonResponse({'error': 'Missing payment ID or OTP code'}, status=400)
        
        # Validate OTP format before database query
        if not OTPSecurityManager.validate_otp_format(otp_code):
            security_logger.warning(f'Invalid OTP format attempted for payment {payment_id}')
            return JsonResponse({'error': 'Invalid OTP format'}, status=400)
        
        # Get payment and OTP
        try:
            payment = Payment.objects.select_related('registration', 'enrollment', 'otp').get(id=payment_id)
            otp = payment.otp
            logger.info(f'OTP Verification Attempt: Payment {payment_id} | DB OTP Code: {otp.otp_code} (length={len(otp.otp_code)}) | Attempts: {otp.attempts}/{settings.OTP_MAX_ATTEMPTS} | Verified: {otp.is_verified}')
        except Payment.DoesNotExist:
            logger.error(f'❌ OTP verification: Payment {payment_id} not found')
            security_logger.warning(f'OTP verification attempted for non-existent payment: {payment_id}')
            return JsonResponse({'error': 'Payment not found'}, status=404)
        except PaymentOTP.DoesNotExist:
            logger.error(f'❌ OTP verification: No OTP record for payment {payment_id}')
            security_logger.error(f'Missing OTP for payment: {payment_id}')
            return JsonResponse({'error': 'OTP not found. Please request a new code'}, status=404)
        
        # Check for lockout
        identifier = f'payment_{payment.id}'
        is_locked, seconds_remaining = OTPSecurityManager.is_locked_out(identifier)
        
        if is_locked:
            security_logger.warning(f'🔒 Locked out payment OTP verification: {payment_id}')
            minutes_remaining = seconds_remaining // 60
            return JsonResponse({
                'error': f'Account temporarily locked due to multiple failed attempts. Please try again in {minutes_remaining} minutes.'
            }, status=429)
        
        # Verify OTP with enhanced security
        success, message = otp.verify_otp(otp_code)
        
        logger.info(f'OTP Verification Result: Entered={otp_code} | Success={success} | Message={message}')
        
        if not success:
            security_logger.warning(f'❌ Failed OTP verification for payment {payment_id}: {message}')
            
            # Check if should lock out
            if otp.attempts >= settings.OTP_MAX_ATTEMPTS:
                OTPSecurityManager.lockout_user(identifier)
            
            return JsonResponse({'error': message}, status=400)
        
        logger.info(f'✅ OTP verified successfully for payment {payment.id}')
        
        if success:
            # Confirm Stripe Payment Intent
            if payment.stripe_payment_intent_id:
                # Retrieve and confirm the intent using the attached payment method from metadata
                stripe_result = StripePaymentProcessor.confirm_payment(payment.stripe_payment_intent_id)
                
                if stripe_result['success']:
                    payment_intent = stripe.PaymentIntent.retrieve(payment.stripe_payment_intent_id)
                    
                    # Update payment with Stripe charge details
                    if payment_intent.charges and payment_intent.charges.data:
                        charge = payment_intent.charges.data[0]
                        payment.stripe_charge_id = charge.id
                    
                    # Update payment status to completed
                    payment.status = 'completed'
                    payment.completed_at = timezone.now()
                    payment.save()
                    
                    # Generate invoice number and create invoice
                    payment.generate_invoice_number()
                    payment.save()
                    
                    # Ensure invoice record exists
                    if not hasattr(payment, 'invoice'):
                        PaymentInvoice.objects.create(payment=payment)

                    # Generate and save PDF invoice safely
                    try:
                        pdf_bytes = generate_invoice_pdf(payment)
                        pdf_filename = f"invoice_{payment.invoice_number}.pdf"
                        payment.invoice.invoice_pdf.save(pdf_filename, ContentFile(pdf_bytes), save=False)
                        payment.invoice.save()
                    except Exception as pdf_err:
                        logger.error(f"❌ Failed to generate/save invoice PDF for payment {payment.id}: {pdf_err}")
                    
                    # Send payment confirmation email with invoice
                    try:
                        subject = 'Payment Confirmed & Invoice - OncoOne'
                        message = f"""
Dear {payment.registration.name},

Thank you for your payment! Your payment has been successfully processed.

📋 Payment Details:
- Invoice Number: {payment.invoice_number}
- Course: {payment.course_name}
- Amount Paid: CAD ${payment.payment_amount_cad}
- Tax (5% GST): CAD ${payment.tax_amount}
- Total: CAD ${payment.final_amount_cad}
- Remaining Balance: CAD ${payment.calculate_remaining_balance()}
- Payment Date: {payment.completed_at.strftime('%Y-%m-%d %H:%M:%S')}
- Card: {payment.payment_method.upper()} ending in {payment.card_last_four}

Your invoice is attached to this email.

Best regards,
OncoOne Team
info@oncoesthetics.ca
                        """
                        
                        email_obj = EmailMessage(
                            subject=subject,
                            body=message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            to=[payment.registration.email]
                        )
                        
                        # Attach PDF invoice
                        email_obj.attach(
                            pdf_filename,
                            pdf_bytes,
                            'application/pdf'
                        )
                        
                        email_obj.send(fail_silently=True)
                    except Exception as e:
                        print(f"Failed to send confirmation email: {e}")
                    
                    return JsonResponse({
                        'status': 'success',
                        'payment_id': payment.id,
                        'invoice_number': payment.invoice_number,
                        'message': 'Payment verified and confirmed successfully!'
                    })
                else:
                    # If 3DS or further action is required, surface info to client
                    return JsonResponse({
                        'status': 'error',
                        'stripe_status': stripe_result.get('status'),
                        'requires_action': stripe_result.get('requires_action'),
                        'client_secret': stripe_result.get('client_secret'),
                        'message': stripe_result.get('error', 'Failed to confirm payment. Please try again.')
                    }, status=400)
            else:
                # Fallback for non-Stripe payments
                payment.status = 'completed'
                payment.completed_at = timezone.now()
                payment.save()
                
                return JsonResponse({
                    'status': 'success',
                    'payment_id': payment.id,
                    'message': 'OTP verified successfully'
                })
        else:
            return JsonResponse({
                'status': 'error',
                'message': message
            }, status=400)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"Error verifying OTP: {e}")
        return JsonResponse({'error': 'An error occurred. Please try again.'}, status=500)


def payment_otp_verification_page(request, payment_id):
    """Display OTP verification page"""
    try:
        payment = Payment.objects.get(id=payment_id, status='pending')
        student = payment.registration
        
        context = {
            'payment_id': payment_id,
            'student_id': student.id,
            'student_name': student.name,
            'student_email': student.email,
            'course': payment.course_name,
            'payment_amount': payment.payment_amount_cad,
            'tax_amount': payment.tax_amount,
            'total_amount': payment.final_amount_cad,
            'card_last_four': payment.card_last_four,
            'card_type': payment.payment_method.upper()
        }
        return render(request, 'payments/payment_otp_verification.html', context)
    except Payment.DoesNotExist:
        return render(request, 'payments/payment_cancelled.html', {
            'error': 'Payment not found or already verified'
        }, status=404)


# Removed duplicate legacy student_login (form POST). JSON-based version above is authoritative.


def student_dashboard(request, student_id):
    """Display student payment history with filters and invoice downloads"""
    try:
        student = Registration.objects.get(id=student_id)
    except Registration.DoesNotExist:
        return redirect('student-login')

    # Filters from query params
    selected_course = request.GET.get('course', 'all')
    selected_status = request.GET.get('status', 'all')

    # Base queryset
    payments_qs = Payment.objects.filter(registration=student)
    if selected_course and selected_course != 'all':
        payments_qs = payments_qs.filter(course_name=selected_course)
    if selected_status and selected_status != 'all':
        payments_qs = payments_qs.filter(status=selected_status)

    payments_qs = payments_qs.order_by('-created_at')

    # Enrollment and course options
    enrollments = StudentCourseEnrollment.objects.filter(registration=student)
    course_names = sorted({e.course_name for e in enrollments})

    # Totals
    from django.db.models import Sum
    # Total paid should exclude tax (use pre-tax amount applied to fee)
    total_paid = payments_qs.filter(status='completed').aggregate(s=Sum('payment_amount_cad'))['s'] or 0
    payment_count = payments_qs.count()

    # Remaining balance: respect selected course filter
    remaining_balance = 0.0
    if selected_course and selected_course != 'all':
        filtered_enrollments = [e for e in enrollments if e.course_name == selected_course]
    else:
        filtered_enrollments = list(enrollments)

    for e in filtered_enrollments:
        course_price = CoursePrice.objects.filter(course_name=e.course_name).first()
        full_price = float(course_price.price_cad) if course_price else 0.0
        # Subtract only the pre-tax portion applied to course fee
        paid_sum = Payment.objects.filter(enrollment=e, status='completed').aggregate(p=Sum('payment_amount_cad'))['p'] or 0
        remaining_balance += max(full_price - float(paid_sum), 0.0)

    context = {
        'student': student,
        'student_name': student.name,
        'registration_id': student.registration_id,
        'student_id': student.id,
        'payments': payments_qs,  # pass model instances so template helpers work
        'enrollments': enrollments,
        'course_options': course_names,
        'selected_course': selected_course,
        'selected_status': selected_status,
        'total_paid': float(total_paid),
        'remaining_balance': float(remaining_balance),
        'payment_count': payment_count,
    }

    return render(request, 'payments/student_dashboard.html', context)


def download_payment_invoice(request, payment_id):
    """Download payment invoice as HTML"""
    try:
        payment = Payment.objects.get(id=payment_id)
        student = payment.registration
        
        # Generate invoice HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .invoice-container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; border-bottom: 3px solid #007bff; padding-bottom: 20px; }}
                .header h1 {{ color: #333; margin: 0; font-size: 28px; }}
                .header p {{ color: #666; margin: 5px 0; }}
                .invoice-details {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }}
                .detail-box {{ border: 1px solid #ddd; padding: 15px; border-radius: 5px; }}
                .detail-box h3 {{ margin-top: 0; color: #333; font-size: 14px; text-transform: uppercase; }}
                .detail-row {{ margin: 8px 0; }}
                .label {{ font-weight: bold; color: #555; display: inline-block; width: 120px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th {{ background-color: #f9f9f9; padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-weight: bold; color: #333; }}
                td {{ padding: 12px; border-bottom: 1px solid #eee; }}
                .total-row {{ font-weight: bold; background-color: #f0f8ff; }}
                .amount {{ text-align: right; }}
                .status-badge {{ 
                    display: inline-block;
                    padding: 6px 12px; 
                    border-radius: 20px; 
                    color: white;
                    font-weight: bold;
                    font-size: 12px;
                }}
                .status-completed {{ background-color: #28a745; }}
                .status-pending {{ background-color: #ffc107; color: #333; }}
                .status-failed {{ background-color: #dc3545; }}
                .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #999; font-size: 12px; }}
                .company-name {{ color: #007bff; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="invoice-container">
                <div class="header">
                    <h1>PAYMENT INVOICE</h1>
                    <p><span class="company-name">Oncoone Education</span></p>
                    <p>Invoice #: <strong>{payment.invoice_number}</strong></p>
                </div>
                
                <div class="invoice-details">
                    <div class="detail-box">
                        <h3>Student Information</h3>
                        <div class="detail-row">
                            <span class="label">Name:</span> {student.name}
                        </div>
                        <div class="detail-row">
                            <span class="label">Email:</span> {student.email}
                        </div>
                        <div class="detail-row">
                            <span class="label">Phone:</span> {student.contact}
                        </div>
                        <div class="detail-row">
                            <span class="label">Registration:</span> {student.registration_id}
                        </div>
                    </div>
                    
                    <div class="detail-box">
                        <h3>Payment Information</h3>
                        <div class="detail-row">
                            <span class="label">Course:</span> {payment.course_name}
                        </div>
                        <div class="detail-row">
                            <span class="label">Status:</span> <span class="status-badge status-{payment.status}">{payment.get_status_display()}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Method:</span> {(payment.payment_method or '').upper()}
                        </div>
                        <div class="detail-row">
                            <span class="label">Date:</span> {payment.completed_at.strftime('%b %d, %Y %H:%M') if payment.completed_at else 'Pending'}
                        </div>
                    </div>
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>Description</th>
                            <th class="amount">Amount (CAD)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>{payment.course_name} - Course Fee</td>
                            <td class="amount">${payment.total_price_cad:.2f}</td>
                        </tr>
                        <tr>
                            <td>Payment Received</td>
                            <td class="amount">${payment.payment_amount_cad:.2f}</td>
                        </tr>
                        <tr>
                            <td>HST/GST Tax (5%)</td>
                            <td class="amount">${payment.tax_amount:.2f}</td>
                        </tr>
                        <tr class="total-row">
                            <td>Total Amount Paid</td>
                            <td class="amount">${payment.final_amount_cad:.2f}</td>
                        </tr>
                    </tbody>
                </table>
                
                <div class="footer">
                    <p><strong>Payment Details:</strong></p>
                    <p>Transaction ID: {payment.transaction_id}</p>
                    <p>Card Ending In: {payment.card_last_four}</p>
                    <p style="margin-top: 20px; color: #666;">Thank you for your payment. This invoice was generated on {payment.completed_at.strftime('%B %d, %Y') if payment.completed_at else 'N/A'}</p>
                    <p style="color: #999; font-size: 11px;">This is an automatically generated document and is valid without a signature.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        response = HttpResponse(html, content_type='text/html')
        response['Content-Disposition'] = f'attachment; filename="Invoice_{payment.invoice_number}.html"'
        return response
    except Payment.DoesNotExist:
        return HttpResponse('Invoice not found', status=404)


@staff_member_required
def admin_generate_invoice(request, payment_id):
    """Generate and persist an invoice (PDF + HTML) for an existing payment.
    Useful when payments were inserted manually in the DB.
    """
    try:
        payment = Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        return HttpResponse('Payment not found', status=404)

    # Only generate for completed payments
    if payment.status != 'completed':
        return HttpResponse('Invoice can only be generated for completed payments', status=400)

    # Ensure invoice number exists
    if not payment.invoice_number:
        payment.generate_invoice_number()
        payment.save()

    # Create or get invoice record
    invoice, _created = PaymentInvoice.objects.get_or_create(payment=payment)

    # HTML snapshot
    invoice.invoice_html = f"Invoice {payment.invoice_number} for {payment.registration.name} ({payment.course_name})"

    # PDF bytes
    pdf_bytes = generate_invoice_pdf(payment)
    pdf_filename = f"invoice_{payment.invoice_number}.pdf"
    invoice.invoice_pdf.save(pdf_filename, ContentFile(pdf_bytes), save=False)
    invoice.save()

    return HttpResponse(f'Invoice generated for {payment.invoice_number}', status=200)

