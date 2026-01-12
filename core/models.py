from django.db import models
from django.utils import timezone
from decimal import Decimal
import uuid
import random
import string


class Course(models.Model):
	"""Master course catalog - all available courses"""
	
	course_name = models.CharField(max_length=255, unique=True)
	course_code = models.CharField(max_length=50, unique=True)  # e.g., "OEC", "BRIDGE"
	description = models.TextField(blank=True, null=True)
	price_cad = models.DecimalField(max_digits=10, decimal_places=2)
	duration_weeks = models.IntegerField(blank=True, null=True)  # Course duration
	requires_prerequisite = models.BooleanField(default=False)  # Does this course require proof?
	is_active = models.BooleanField(default=True)  # Active/Inactive courses
	
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['course_name']
		verbose_name = 'Course'
		verbose_name_plural = 'Courses'

	def __str__(self):
		return f"{self.course_name} ({self.course_code})"


class Registration(models.Model):
	"""Student registration model - single student can register for multiple courses"""
	
	name = models.CharField(max_length=255)
	email = models.EmailField(unique=True, db_index=True)  # Prevent duplicate emails
	contact = models.CharField(max_length=50)
	registration_number = models.CharField(max_length=20, unique=True, db_index=True, blank=True, default='')  # ON26-0001 format
	student_password = models.CharField(max_length=10, unique=True, blank=True, default='')  # Unique 10-character password
	
	# Student info (common across all courses)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']
		verbose_name = 'Student Registration'
		verbose_name_plural = 'Student Registrations'

	def __str__(self):
		return f"{self.registration_number} - {self.name} <{self.email}>"
	
	@staticmethod
	def generate_registration_number():
		"""Generate unique registration number in format: ON{YY}-{XXXXXX}
		Example: ON26-698574 for a student in 2026 (random 6-digit number)
		"""
		from django.utils import timezone
		import random
		
		current_year = timezone.now().year
		year_suffix = str(current_year)[-2:]  # Last 2 digits (26 for 2026)
		
		# Generate unique random 6-digit number
		max_attempts = 1000
		for _ in range(max_attempts):
			# Generate random 6-digit number (100000 to 999999)
			random_num = random.randint(100000, 999999)
			registration_number = f"ON{year_suffix}-{random_num}"
			
			# Check if this number is already used
			if not Registration.objects.filter(registration_number=registration_number).exists():
				return registration_number
		
		# If somehow we couldn't generate unique number after max attempts,
		# fallback to timestamp-based generation
		timestamp = str(int(timezone.now().timestamp()))[-6:]
		registration_number = f"ON{year_suffix}-{timestamp}"
		
		# Ensure uniqueness
		while Registration.objects.filter(registration_number=registration_number).exists():
			random_num = random.randint(100000, 999999)
			registration_number = f"ON{year_suffix}-{random_num}"
		
		return registration_number
	
	def generate_unique_password(self):
		"""Generate a unique 10-character password for the student"""
		# Generate until we get a unique one
		max_attempts = 100
		for _ in range(max_attempts):
			# Mix of uppercase, lowercase, digits, and special chars
			chars = string.ascii_uppercase + string.ascii_lowercase + string.digits + "!@#$%^&*"
			password = ''.join(random.choice(chars) for _ in range(10))
			
			# Check if password is unique
			if not Registration.objects.filter(student_password=password).exists():
				return password
		
		# If still no unique password after max attempts, add timestamp
		timestamp = str(int(timezone.now().timestamp()))[-4:]
		chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
		password = ''.join(random.choice(chars) for _ in range(6)) + timestamp
		return password
	
	def save(self, *args, **kwargs):
		"""Auto-generate registration number and password if not set"""
		if not self.registration_number:
			self.registration_number = self.generate_registration_number()
		
		if not self.student_password:
			self.student_password = self.generate_unique_password()
		
		super().save(*args, **kwargs)
	
	def get_enrolled_courses(self):
		"""Get all courses this student is enrolled in"""
		return StudentCourseEnrollment.objects.filter(registration=self)


class StudentCourseEnrollment(models.Model):
	"""Track each course enrollment for a student (allows multiple courses per student)
	Many-to-many relationship: 1 student can enroll in many courses, 1 course can have many students"""
	
	registration = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name='course_enrollments')
	course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='enrollments', null=True, blank=True)  # Reference to Course model
	
	# Legacy field for backward compatibility (will be deprecated)
	course_name = models.CharField(max_length=255, blank=True, null=True)
	
	has_prerequisite = models.BooleanField(default=True)  # True = has cert/proof, False = needs bridge course
	
	# Proof of prerequisite (only required if has_prerequisite=True)
	proof = models.FileField(upload_to='proofs/', blank=True, null=True)
	proof_name = models.CharField(max_length=255, blank=True, null=True)
	proof_mime = models.CharField(max_length=100, blank=True, null=True)
	proof_data = models.BinaryField(blank=True, null=True)
	
	enrollment_status = models.CharField(
		max_length=20,
		choices=[
			('pending', 'Pending'),
			('approved', 'Approved'),
			('in_progress', 'In Progress'),
			('completed', 'Completed'),
		],
		default='pending'
	)
	
	enrolled_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = ['registration', 'course']  # Prevent duplicate enrollments for same course
		ordering = ['-enrolled_at']
		verbose_name = 'Course Enrollment'
		verbose_name_plural = 'Course Enrollments'

	def __str__(self):
		return f"{self.registration.registration_number} - {self.course.course_name}"
	
	def save(self, *args, **kwargs):
		"""Auto-populate course_name for backward compatibility"""
		if self.course:
			self.course_name = self.course.course_name
		super().save(*args, **kwargs)


class Payment(models.Model):
	"""Store payment transactions - links to specific course enrollment"""
	PAYMENT_STATUS_CHOICES = [
		('pending', 'Pending'),
		('processing', 'Processing'),
		('completed', 'Completed'),
		('failed', 'Failed'),
		('cancelled', 'Cancelled'),
	]

	registration = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name='payments')
	enrollment = models.ForeignKey(StudentCourseEnrollment, on_delete=models.CASCADE, related_name='payments', blank=True, null=True)
	student_id = models.CharField(max_length=50)  # student/registration ID
	course_name = models.CharField(max_length=255)
	total_price_cad = models.DecimalField(max_digits=10, decimal_places=2)  # Original course price
	payment_amount_cad = models.DecimalField(max_digits=10, decimal_places=2)  # Amount user wants to pay
	tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	final_amount_cad = models.DecimalField(max_digits=10, decimal_places=2)  # Total with tax
	status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
	
	# Payment method and card details
	payment_method = models.CharField(max_length=50, blank=True, null=True)  # visa, mastercard
	card_holder_name = models.CharField(max_length=255, blank=True, null=True)
	card_last_four = models.CharField(max_length=4, blank=True, null=True)  # Last 4 digits for security
	
	# Stripe Payment Fields
	stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)  # Stripe PI ID
	stripe_charge_id = models.CharField(max_length=255, blank=True, null=True)  # Stripe Charge ID
	stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)  # Stripe Customer ID
	
	# Transaction reference
	transaction_id = models.CharField(max_length=100, blank=True, null=True)
	
	# Invoice and tracking
	invoice_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
	
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	completed_at = models.DateTimeField(blank=True, null=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"Payment {self.invoice_number} - {self.student_id} - {self.status}"

	def generate_invoice_number(self):
		"""Generate a unique invoice number"""
		from datetime import datetime
		if not self.invoice_number:
			timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
			random_suffix = str(self.id).zfill(5)
			self.invoice_number = f"INV-{timestamp}-{random_suffix}"

	def calculate_remaining_balance(self):
		"""Calculate remaining balance for the course"""
		return self.total_price_cad - self.payment_amount_cad
	
	def get_status_display(self):
		"""Get human-readable status"""
		for value, label in self.PAYMENT_STATUS_CHOICES:
			if value == self.status:
				return label
		return self.status


class PaymentInvoice(models.Model):
	"""Store generated invoices for successful payments"""
	payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='invoice')
	invoice_pdf = models.FileField(upload_to='invoices/', blank=True, null=True)
	invoice_html = models.TextField(blank=True, null=True)
	generated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Invoice for {self.payment.invoice_number}"


class PaymentOTP(models.Model):
	"""Store OTP for secure payment verification with rate limiting"""
	payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='otp')
	otp_code = models.CharField(max_length=6, db_index=True)
	is_verified = models.BooleanField(default=False, db_index=True)
	attempts = models.IntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True, db_index=True)
	expires_at = models.DateTimeField(db_index=True)  # OTP valid for configurable time
	verified_at = models.DateTimeField(blank=True, null=True)
	ip_address = models.GenericIPAddressField(blank=True, null=True)  # Track IP for security

	class Meta:
		ordering = ['-created_at']
		indexes = [
			models.Index(fields=['payment', 'is_verified']),
			models.Index(fields=['expires_at', 'is_verified']),
		]

	def __str__(self):
		return f"OTP for Payment {self.payment.invoice_number or self.payment.id}"

	def generate_otp(self):
		"""Generate a secure 6-digit OTP using payment_security module"""
		from .payment_security import OTPSecurityManager
		self.otp_code = OTPSecurityManager.generate_otp_code()

	def is_expired(self):
		"""Check if OTP has expired"""
		return timezone.now() > self.expires_at

	def verify_otp(self, entered_otp: str) -> tuple:
		"""
		Verify OTP with comprehensive security checks
		
		Args:
			entered_otp: The OTP code entered by user
			
		Returns:
			tuple: (success: bool, message: str)
		"""
		from django.conf import settings
		from .payment_security import OTPSecurityManager
		
		# Check if already verified
		if self.is_verified:
			return False, "This OTP has already been used"
		
		# Validate OTP format
		if not OTPSecurityManager.validate_otp_format(entered_otp):
			return False, "Invalid OTP format. Please enter a 6-digit code"
		
		# Check expiration
		if self.is_expired():
			return False, "OTP has expired. Please request a new code"
		
		# Check maximum attempts
		max_attempts = getattr(settings, 'OTP_MAX_ATTEMPTS', 3)
		if self.attempts >= max_attempts:
			return False, f"Maximum verification attempts ({max_attempts}) exceeded. Please request a new OTP"
		
		# Check rate limiting
		identifier = f"payment_{self.payment.id}"
		is_allowed, remaining = OTPSecurityManager.check_rate_limit(identifier)
		
		if not is_allowed:
			return False, "Too many attempts. Please try again later"
		
		# Increment attempts
		self.attempts += 1
		self.save(update_fields=['attempts'])
		
		# Verify OTP code
		if entered_otp.strip() == self.otp_code:
			self.is_verified = True
			self.verified_at = timezone.now()
			self.save(update_fields=['is_verified', 'verified_at'])
			
			# Record successful attempt
			OTPSecurityManager.record_otp_attempt(identifier, success=True)
			
			return True, "OTP verified successfully"
		
		# Failed attempt
		OTPSecurityManager.record_otp_attempt(identifier, success=False)
		
		remaining_attempts = max_attempts - self.attempts
		
		if remaining_attempts > 0:
			return False, f"Invalid OTP code. {remaining_attempts} attempt(s) remaining"
		else:
			return False, "Invalid OTP. Maximum attempts reached. Please request a new code"

