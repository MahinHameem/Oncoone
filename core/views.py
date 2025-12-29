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
import json
import uuid


from .models import Registration, Payment, CoursePrice, PaymentInvoice, PaymentOTP
from .stripe_processor import StripePaymentProcessor


@csrf_exempt
def register_view(request):
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)

    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    contact = request.POST.get('contact', '').strip()
    course = request.POST.get('course', '').strip() or 'Course'
    auto_bridge = request.POST.get('autoBridge', 'false').lower() in ('1', 'true', 'yes')
    proof = request.FILES.get('proof')

    if not (name and email and contact):
        return HttpResponseBadRequest('Missing required fields')

    # ✅ Check for duplicate email registration
    if Registration.objects.filter(email=email).exists():
        return JsonResponse({
            'status': 'error',
            'error': 'This email has already been registered. Please use a different email or contact support if you need to update your registration.',
            'existing_registration': True
        }, status=400)

    # read uploaded file bytes for DB storage (if provided)
    proof_bytes = None
    proof_name = None
    proof_mime = None
    # validate uploaded file (type + size) before reading into DB
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
            # rewind uploaded file so assigning it to model.FileField still saves correctly
            try:
                proof.seek(0)
            except Exception:
                pass
        except Exception:
            proof_bytes = None

    reg = Registration.objects.create(
        name=name,
        email=email,
        contact=contact,
        course=course,
        auto_bridge=auto_bridge,
        proof=proof if proof else None,
        proof_name=proof_name,
        proof_mime=proof_mime,
        proof_data=proof_bytes,
    )

    # Send admin notification email (attach proof if present)
    admin_email = getattr(settings, 'ADMIN_EMAIL', '')
    subject = f'New registration: {reg.name} for {reg.course}'
    body = f"Name: {reg.name}\nEmail: {reg.email}\nContact: {reg.contact}\nCourse: {reg.course}\nRegistration ID: {reg.registration_id}\nAuto bridge: {reg.auto_bridge}\nSubmitted: {reg.created_at}\n"

    if admin_email:
        try:
            email_msg = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [admin_email])
            if reg.proof:
                # read file content and attach; derive mime safely
                reg.proof.open()
                mime = None
                if hasattr(reg.proof, 'file') and hasattr(reg.proof.file, 'content_type'):
                    mime = reg.proof.file.content_type
                elif reg.proof_mime:
                    mime = reg.proof_mime
                email_msg.attach(reg.proof.name.split('/')[-1], reg.proof.read(), mime)
                reg.proof.close()
            email_msg.send(fail_silently=True)
        except Exception as exc:  # silently handle admin email errors, don't block registration
            print(f"Email send failed: {exc}")

    # Send confirmation email to the registrant with registration ID
    if reg.email:
        try:
            user_subject = f"Welcome to OncoOne - Your Registration ID: {reg.registration_id}"
            user_body = (
                f"Hi {reg.name},\n\n"
                f"Thank you for registering for {reg.course}. We have received your details and will be in touch shortly.\n\n"
                f"Your Registration ID: {reg.registration_id}\n"
                f"Email: {reg.email}\n\n"
                f"You can use your Registration ID to access the payment portal and track your payments.\n\n"
                f"If you have questions, reply to this email.\n\n"
                f"– OncoOne Team"
            )
            EmailMessage(user_subject, user_body, settings.DEFAULT_FROM_EMAIL, [reg.email]).send(fail_silently=True)
        except Exception:
            # don't block flow if user confirmation fails
            pass

    return JsonResponse({
        'status': 'ok',
        'id': reg.id,
        'registration_id': reg.registration_id,
        'message': f'Registration successful! Your Registration ID is: {reg.registration_id}'
    })


# Admin API: list, edit, delete registrations (development use only)
@csrf_exempt
def registrations_list(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    regs = Registration.objects.order_by('-created_at').all()
    data = []
    for r in regs:
        proof_url = None
        if r.proof:
            try:
                proof_url = request.build_absolute_uri(r.proof.url)
            except Exception:
                proof_url = None
        has_db_proof = bool(r.proof_data)
        download_url = request.build_absolute_uri(f'/api/admin/registrations/{r.id}/download/')
        data.append({
            'id': r.id,
            'name': r.name,
            'email': r.email,
            'contact': r.contact,
            'course': r.course,
            'auto_bridge': r.auto_bridge,
            'created_at': r.created_at.isoformat(),
            'has_db_proof': has_db_proof,
            'download_url': download_url,
        })
    return JsonResponse({'results': data})


@csrf_exempt
def registration_detail(request, pk):
    reg = get_object_or_404(Registration, pk=pk)

    if request.method == 'GET':
        has_db_proof = bool(reg.proof_data)
        download_url = request.build_absolute_uri(f'/api/admin/registrations/{reg.id}/download/')
        return JsonResponse({
            'id': reg.id,
            'name': reg.name,
            'email': reg.email,
            'contact': reg.contact,
            'course': reg.course,
            'auto_bridge': reg.auto_bridge,
            'created_at': reg.created_at.isoformat(),
            'has_db_proof': has_db_proof,
            'download_url': download_url,
        })

    if request.method in ('PUT', 'PATCH'):
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except Exception:
            return HttpResponseBadRequest('Invalid JSON')

        changed = False
        for field in ('name', 'email', 'contact', 'course'):
            if field in payload:
                setattr(reg, field, payload[field])
                changed = True
        if 'auto_bridge' in payload:
            reg.auto_bridge = bool(payload['auto_bridge'])
            changed = True
        if changed:
            reg.save()
        return JsonResponse({'status': 'ok'})

    if request.method == 'DELETE':
        # delete attached file from storage
        if reg.proof:
            try:
                reg.proof.delete(save=False)
            except Exception:
                pass
        reg.delete()
        return JsonResponse({'status': 'deleted'})

    return HttpResponseNotAllowed(['GET', 'PUT', 'PATCH', 'DELETE'])


@staff_member_required
def download_proof_db(request, pk):
    reg = get_object_or_404(Registration, pk=pk)
    if not reg.proof_data:
        return HttpResponse(status=404)
    # stream DB bytes as attachment
    resp = HttpResponse(reg.proof_data, content_type=reg.proof_mime or 'application/octet-stream')
    filename = reg.proof_name or f'registration-{reg.id}-proof'
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp


@staff_member_required
def download_proof(request, pk):
    """Serve attached proof whether stored in DB (`proof_data`) or on disk (`proof`)."""
    reg = get_object_or_404(Registration, pk=pk)
    # Prefer DB-stored bytes
    if reg.proof_data:
        resp = HttpResponse(reg.proof_data, content_type=reg.proof_mime or 'application/octet-stream')
        filename = reg.proof_name or f'registration-{reg.id}-proof'
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        return resp

    # Fallback to FileField on-disk file
    if reg.proof:
        try:
            # use FileResponse for efficient file streaming
            from django.http import FileResponse
            reg.proof.open('rb')
            filename = reg.proof.name.split('/')[-1]
            response = FileResponse(reg.proof, as_attachment=True, filename=filename)
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
		
		# Get courses registered by this student
		courses = [registration.course]
		
		# Get course prices
		course_data = []
		for course in courses:
			course_price = CoursePrice.objects.filter(course_name=course).first()
			if course_price:
				course_data.append({
					'id': course_price.id,
					'name': course,
					'price': str(course_price.price_cad),
					'description': course_price.description or ''
				})
			else:
				# If no price set, show placeholder
				course_data.append({
					'id': None,
					'name': course,
					'price': '0.00',
					'description': 'Price not set'
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
	
	# Get course price
	course_price = CoursePrice.objects.filter(course_name=registration.course).first()
	price = course_price.price_cad if course_price else Decimal('0.00')
	
	context = {
		'student': registration,
		'course': registration.course,
		'total_price': float(price),
		'currency': 'CAD'
	}
	
	return render(request, 'payments/payment_select_amount.html', context)


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
	
	# Get values from session or query params
	payment_amount = request.GET.get('amount', '0')
	tax_amount = request.GET.get('tax', '0')
	total_amount = request.GET.get('total', '0')
	
	course_price = CoursePrice.objects.filter(course_name=registration.course).first()
	course_full_price = float(course_price.price_cad) if course_price else 0.00
	remaining_balance = float(course_price.price_cad) - float(payment_amount) if course_price else 0.00
	
	context = {
		'student': registration,
		'student_id': registration.id,
		'course': registration.course,
		'payment_amount': float(payment_amount),
		'tax_amount': float(tax_amount),
		'total_amount': float(total_amount),
		'course_full_price': course_full_price,
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
	
	payment_amount = request.GET.get('amount', '0')
	tax_amount = request.GET.get('tax', '0')
	total_amount = request.GET.get('total', '0')
	
	context = {
		'student': registration,
		'student_id': registration.id,
		'student_email': registration.email,
		'course': registration.course,
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
		
		# Extract last 4 digits of card
		card_last_four = card_number[-4:] if len(card_number) >= 4 else card_number
		
		# Create payment record
		payment = Payment.objects.create(
			registration=registration,
			student_id=str(student_id),
			course_name=registration.course,
			total_price_cad=CoursePrice.objects.filter(course_name=registration.course).first().price_cad or Decimal('0.00'),
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
					<span>{registration.course}</span>
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
Course: {registration.course}
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

def student_login(request):
	"""Student login page using Registration ID or Email"""
	if request.method == 'GET':
		# Return login page
		return render(request, 'payments/student_login.html')
	
	elif request.method == 'POST':
		# Handle JSON login request
		try:
			data = json.loads(request.body)
		except json.JSONDecodeError:
			return JsonResponse({'status': 'error', 'error': 'Invalid request'}, status=400)
		
		# Extract login credentials
		registration_id = data.get('registration_id', '').strip()
		email = data.get('email', '').strip()
		student_id = data.get('student_id', '').strip()
		
		# Find student by Registration ID, email, or numeric ID
		student = None
		
		if registration_id:
			# Parse Registration ID format (REG-YYYYMMDD-XXXXXX)
			if registration_id.startswith('REG-'):
				try:
					parts = registration_id.split('-')
					if len(parts) == 3:
						numeric_id = int(parts[2])
						student = Registration.objects.filter(id=numeric_id).first()
				except (ValueError, IndexError):
					pass
			if not student:
				# Try as direct lookup if format doesn't match
				try:
					student = Registration.objects.get(id=int(registration_id))
				except (ValueError, Registration.DoesNotExist):
					pass
		
		if not student and email:
			student = Registration.objects.filter(email=email).first()
		
		if not student and student_id:
			try:
				student_id_int = int(student_id)
				student = Registration.objects.get(id=student_id_int)
			except (ValueError, Registration.DoesNotExist):
				pass
		
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
				'error': 'Registration ID, email, or student ID not found. Please check your credentials and try again.'
			}, status=404)


def student_logout(request):
	"""Student logout"""
	request.session.flush()
	return redirect('student-login')


def student_dashboard(request):
	"""Student dashboard showing payment history"""
	student_id = request.session.get('student_id')
	
	if not student_id:
		return redirect('student-login')
	
	try:
		student = Registration.objects.get(id=student_id)
	except Registration.DoesNotExist:
		request.session.flush()
		return redirect('student-login')
	
	# Get all payments for this student
	payments = Payment.objects.filter(registration=student).order_by('-created_at')
	
	# Calculate summary
	total_paid = sum(float(p.final_amount_cad) for p in payments if p.status == 'completed')
	course_fee = CoursePrice.objects.filter(course_name=student.course).first()
	course_fee_amount = float(course_fee.price_cad) if course_fee else 0
	remaining_balance = course_fee_amount - total_paid
	
	context = {
		'student': student,
		'payments': payments,
		'total_paid': total_paid,
		'course_fee': course_fee_amount,
		'remaining_balance': max(remaining_balance, 0),
		'payment_count': payments.count(),
		'completed_payment_count': payments.filter(status='completed').count(),
	}
	
	return render(request, 'payments/student_dashboard.html', context)


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
	"""Generate professional PDF invoice for payment"""
	from reportlab.lib.pagesizes import letter
	from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
	from reportlab.lib.units import inch
	from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
	from reportlab.lib import colors
	from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
	from io import BytesIO
	
	# Create PDF in memory
	pdf_buffer = BytesIO()
	doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
	
	# Styles
	styles = getSampleStyleSheet()
	title_style = ParagraphStyle(
		'CustomTitle',
		parent=styles['Heading1'],
		fontSize=24,
		textColor=colors.HexColor('#667eea'),
		spaceAfter=0,
		alignment=TA_CENTER,
		fontName='Helvetica-Bold'
	)
	
	heading_style = ParagraphStyle(
		'CustomHeading',
		parent=styles['Heading2'],
		fontSize=12,
		textColor=colors.HexColor('#333333'),
		spaceAfter=12,
		fontName='Helvetica-Bold'
	)
	
	normal_style = ParagraphStyle(
		'CustomNormal',
		parent=styles['Normal'],
		fontSize=10,
		textColor=colors.HexColor('#333333'),
	)
	
	# Content
	elements = []
	
	# Header
	elements.append(Paragraph("OncoOne Online Payments Portal", title_style))
	elements.append(Paragraph("PAYMENT INVOICE", heading_style))
	elements.append(Spacer(1, 0.2*inch))
	
	# Invoice details header
	invoice_data = [
		['Invoice Number', payment.invoice_number],
		['Date', payment.completed_at.strftime('%Y-%m-%d %H:%M:%S')],
		['Transaction ID', payment.transaction_id],
	]
	
	invoice_table = Table(invoice_data, colWidths=[2*inch, 3*inch])
	invoice_table.setStyle(TableStyle([
		('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
		('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
		('ALIGN', (0, 0), (-1, -1), 'LEFT'),
		('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
		('FONTSIZE', (0, 0), (-1, -1), 9),
		('BOTTOMPADDING', (0, 0), (-1, -1), 8),
		('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
	]))
	elements.append(invoice_table)
	elements.append(Spacer(1, 0.3*inch))
	
	# Student Information
	elements.append(Paragraph("Student Information", heading_style))
	student_data = [
		['Field', 'Details'],
		['Student ID', str(payment.registration.id)],
		['Registration ID', payment.registration.registration_id],
		['Name', payment.registration.name],
		['Email', payment.registration.email],
		['Contact', payment.registration.contact],
	]
	
	student_table = Table(student_data, colWidths=[2*inch, 3*inch])
	student_table.setStyle(TableStyle([
		('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
		('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
		('ALIGN', (0, 0), (-1, -1), 'LEFT'),
		('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
		('FONTSIZE', (0, 0), (-1, -1), 9),
		('BOTTOMPADDING', (0, 0), (-1, -1), 8),
		('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
		('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
	]))
	elements.append(student_table)
	elements.append(Spacer(1, 0.3*inch))
	
	# Payment Details
	elements.append(Paragraph("Payment Details", heading_style))
	payment_data = [
		['Description', 'Amount (CAD)'],
		['Course', payment.course_name],
		['Full Course Fee', f"${payment.total_price_cad:.2f}"],
		['Payment Amount', f"${payment.payment_amount_cad:.2f}"],
		['Tax (5% GST)', f"${payment.tax_amount:.2f}"],
		['Total Paid', f"${payment.final_amount_cad:.2f}"],
		['Remaining Balance', f"${payment.calculate_remaining_balance():.2f}"],
	]
	
	payment_table = Table(payment_data, colWidths=[2.5*inch, 2.5*inch])
	payment_table.setStyle(TableStyle([
		('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
		('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
		('ALIGN', (0, 0), (0, -1), 'LEFT'),
		('ALIGN', (1, 0), (1, -1), 'RIGHT'),
		('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
		('FONTSIZE', (0, 0), (-1, -1), 9),
		('BOTTOMPADDING', (0, 0), (-1, -1), 8),
		('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
		('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
		('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#fffaf0')),
		('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
	]))
	elements.append(payment_table)
	elements.append(Spacer(1, 0.3*inch))
	
	# Payment Method
	elements.append(Paragraph("Payment Method", heading_style))
	method_data = [
		['Card Type', payment.payment_method.upper()],
		['Card (Last 4)', f"•••• •••• •••• {payment.card_last_four}"],
		['Cardholder', payment.card_holder_name],
		['Status', payment.get_status_display()],
	]
	
	method_table = Table(method_data, colWidths=[2*inch, 3*inch])
	method_table.setStyle(TableStyle([
		('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
		('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
		('ALIGN', (0, 0), (-1, -1), 'LEFT'),
		('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
		('FONTSIZE', (0, 0), (-1, -1), 9),
		('BOTTOMPADDING', (0, 0), (-1, -1), 8),
		('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
	]))
	elements.append(method_table)
	elements.append(Spacer(1, 0.4*inch))
	
	# Footer
	footer_style = ParagraphStyle(
		'Footer',
		parent=styles['Normal'],
		fontSize=8,
		textColor=colors.HexColor('#999999'),
		alignment=TA_CENTER,
	)
	elements.append(Paragraph(
		"<br/>Thank you for your payment!<br/>"
		"For inquiries, please contact: support@oncoone.com<br/>"
		"© 2025 OncoOne. All rights reserved.",
		footer_style
	))
	
	# Build PDF
	doc.build(elements)
	pdf_buffer.seek(0)
	return pdf_buffer.getvalue()


@csrf_exempt
def create_payment_and_send_otp(request):
	"""Create payment record with Stripe and send OTP for verification"""
	if request.method != 'POST':
		return JsonResponse({'error': 'Method not allowed'}, status=405)
	
	try:
		data = json.loads(request.body.decode('utf-8'))
		
		student_id = data.get('student_id')
		payment_method_id = data.get('payment_method_id')  # Stripe payment method ID
		payment_amount = Decimal(str(data.get('payment_amount', '0')))
		tax_amount = Decimal(str(data.get('tax_amount', '0')))
		total_amount = Decimal(str(data.get('total_amount', '0')))
		card_holder = data.get('card_holder', '').strip()
		card_type = data.get('card_type', '').lower()
		card_last_four = data.get('card_last_four', '0000')
		email = data.get('email', '').strip()
		
		# Validation
		if not all([student_id, payment_method_id, card_holder, card_type, email]):
			return JsonResponse({'error': 'Missing required payment information'}, status=400)
		
		if card_type not in ['visa', 'mastercard', 'amex']:
			return JsonResponse({'error': 'Invalid card type'}, status=400)
		
		# Get registration
		try:
			student_id_int = int(student_id)
			registration = Registration.objects.get(id=student_id_int)
		except (ValueError, Registration.DoesNotExist):
			return JsonResponse({'error': 'Student not found'}, status=404)
		
		# Get course price
		course_price_obj = CoursePrice.objects.filter(course_name=registration.course).first()
		if not course_price_obj:
			return JsonResponse({'error': 'Course price not found'}, status=404)
		
		# Create Stripe Payment Intent
		stripe_result = StripePaymentProcessor.create_payment_intent(
			amount_cad=total_amount,
			email=email,
			student_name=registration.name,
			course_name=registration.course,
			payment_id=None  # We'll update after creating Payment
		)
		
		if not stripe_result['success']:
			return JsonResponse({'error': f'Payment processing error: {stripe_result["error"]}'}, status=400)
		
		stripe_client_secret = stripe_result['client_secret']
		stripe_payment_intent_id = stripe_result['payment_intent_id']
		
		# Create payment record with 'pending' status (waiting for OTP verification)
		payment = Payment.objects.create(
			registration=registration,
			student_id=str(student_id),
			course_name=registration.course,
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
		
		# Create OTP
		from datetime import timedelta
		otp = PaymentOTP.objects.create(
			payment=payment,
			expires_at=timezone.now() + timedelta(minutes=10)
		)
		otp.generate_otp()
		otp.save()
		
		# Send OTP to student email
		try:
			subject = 'Verify Your OncoOne Payment'
			message = f"""
Dear {registration.name},

To complete your payment of CAD ${total_amount:.2f} for {registration.course}, please enter the following OTP code:

🔐 OTP Code: {otp.otp_code}

This code is valid for 10 minutes.

Payment Details:
- Course: {registration.course}
- Amount: CAD ${total_amount:.2f}
- Card: {card_type.upper()} ending in {card_last_four}

If you did not initiate this payment, please ignore this email.

Best regards,
OncoOne Team
info@oncoesthetics.ca
			"""
			
			email_obj = EmailMessage(
				subject=subject,
				body=message,
				from_email=settings.DEFAULT_FROM_EMAIL,
				to=[registration.email]
			)
			email_obj.send(fail_silently=True)
		except Exception as e:
			print(f"Failed to send OTP email: {e}")
		
		return JsonResponse({
			'success': True,
			'payment_id': payment.id,
			'stripe_client_secret': stripe_client_secret,
			'message': f'OTP sent to {registration.email}. Valid for 10 minutes.'
		})
	
	except json.JSONDecodeError:
		return JsonResponse({'error': 'Invalid JSON'}, status=400)
	except Exception as e:
		print(f"Error creating payment: {e}")
		return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)


@csrf_exempt
def verify_payment_otp(request):
	"""Verify OTP for payment"""
	if request.method != 'POST':
		return JsonResponse({'error': 'Method not allowed'}, status=405)
	
	try:
		data = json.loads(request.body.decode('utf-8'))
		
		payment_id = data.get('payment_id')
		otp_code = data.get('otp_code', '').strip()
		
		if not all([payment_id, otp_code]):
			return JsonResponse({'error': 'Missing payment ID or OTP code'}, status=400)
		
		# Get payment and OTP
		try:
			payment = Payment.objects.get(id=payment_id)
			otp = payment.otp
		except Payment.DoesNotExist:
			return JsonResponse({'error': 'Payment not found'}, status=404)
		except PaymentOTP.DoesNotExist:
			return JsonResponse({'error': 'OTP not found'}, status=404)
		
		# Verify OTP
		success, message = otp.verify_otp(otp_code)
		
		if success:
			# Confirm Stripe Payment Intent
			if payment.stripe_payment_intent_id:
				stripe_result = StripePaymentProcessor.get_payment_intent(payment.stripe_payment_intent_id)
				
				if stripe_result['success']:
					payment_intent = stripe_result['payment_intent']
					
					# Update payment with Stripe charge details
					if payment_intent.charges.data:
						charge = payment_intent.charges.data[0]
						payment.stripe_charge_id = charge.id
					
					# Update payment status to completed
					payment.status = 'completed'
					payment.completed_at = timezone.now()
					payment.save()
					
					# Generate invoice number and create invoice
					payment.generate_invoice_number()
					payment.save()
					
					# Generate and save PDF invoice
					pdf_bytes = generate_invoice_pdf(payment)
					pdf_filename = f"invoice_{payment.invoice_number}.pdf"
					payment.invoice.invoice_pdf.save(pdf_filename, ContentFile(pdf_bytes), save=False)
					payment.invoice.save()
					
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
					return JsonResponse({
						'status': 'error',
						'message': 'Failed to confirm payment. Please try again.'
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
