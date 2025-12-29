from django.db import models
from django.utils import timezone
from decimal import Decimal
import uuid
import random
import string


class Registration(models.Model):
	"""Student registration model"""
	
	name = models.CharField(max_length=255)
	email = models.EmailField(unique=True, db_index=True)  # Prevent duplicate emails
	contact = models.CharField(max_length=50)
	course = models.CharField(max_length=255)
	auto_bridge = models.BooleanField(default=False)
	
	# keep FileField for compatibility, but also store file bytes in DB for small-scale projects
	proof = models.FileField(upload_to='proofs/', blank=True, null=True)
	# DB storage fields
	proof_name = models.CharField(max_length=255, blank=True, null=True)
	proof_mime = models.CharField(max_length=100, blank=True, null=True)
	proof_data = models.BinaryField(blank=True, null=True)
	
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"{self.name} <{self.email}>"
	
	@property
	def registration_id(self):
		"""Generate registration ID on the fly from ID and creation date"""
		if self.id:
			timestamp = self.created_at.strftime('%Y%m%d')
			return f"REG-{timestamp}-{self.id:06d}"
		return None


class CoursePrice(models.Model):
	"""Store course pricing information"""
	course_name = models.CharField(max_length=255, unique=True)
	price_cad = models.DecimalField(max_digits=10, decimal_places=2)
	description = models.TextField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['course_name']

	def __str__(self):
		return f"{self.course_name} - CAD ${self.price_cad}"


class Payment(models.Model):
	"""Store payment transactions"""
	PAYMENT_STATUS_CHOICES = [
		('pending', 'Pending'),
		('processing', 'Processing'),
		('completed', 'Completed'),
		('failed', 'Failed'),
		('cancelled', 'Cancelled'),
	]

	registration = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name='payments')
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
	"""Store OTP for payment verification"""
	payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='otp')
	otp_code = models.CharField(max_length=6)
	is_verified = models.BooleanField(default=False)
	attempts = models.IntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	expires_at = models.DateTimeField()  # OTP valid for 10 minutes
	verified_at = models.DateTimeField(blank=True, null=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"OTP for Payment {self.payment.invoice_number}"

	def generate_otp(self):
		"""Generate a 6-digit OTP"""
		self.otp_code = ''.join(random.choices(string.digits, k=6))

	def is_expired(self):
		"""Check if OTP has expired"""
		return timezone.now() > self.expires_at

	def verify_otp(self, entered_otp):
		"""Verify OTP and update status"""
		if self.is_verified:
			return False, "OTP already verified"
		
		if self.is_expired():
			return False, "OTP has expired. Request a new one."
		
		if self.attempts >= 3:
			return False, "Maximum attempts exceeded. Request a new OTP."
		
		self.attempts += 1
		self.save()
		
		if entered_otp == self.otp_code:
			self.is_verified = True
			self.verified_at = timezone.now()
			self.save()
			return True, "OTP verified successfully"
		
		return False, f"Invalid OTP. {3 - self.attempts} attempts remaining."
