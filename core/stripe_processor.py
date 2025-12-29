"""
Stripe Payment Processing Module for OncoOne
Handles all Stripe API interactions for secure payment processing
"""

import stripe
import os
from decimal import Decimal
from django.conf import settings

# Initialize Stripe with API key
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', settings.STRIPE_SECRET_KEY)

class StripePaymentProcessor:
    """Handle Stripe payment processing"""
    
    @staticmethod
    def get_stripe_amount(amount_cad):
        """Convert CAD amount to cents for Stripe"""
        return int(float(amount_cad) * 100)
    
    @staticmethod
    def create_payment_intent(amount_cad, email, student_name, course_name, payment_id):
        """
        Create a Stripe Payment Intent for the payment
        Returns: payment_intent object with client_secret
        """
        try:
            amount_cents = StripePaymentProcessor.get_stripe_amount(amount_cad)
            
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=os.getenv('STRIPE_CURRENCY', 'cad'),
                email=email,
                description=f"OncoOne Course Payment: {course_name}",
                statement_descriptor=os.getenv('STRIPE_STATEMENT_DESCRIPTOR', 'OncoOne'),
                metadata={
                    'payment_id': payment_id,
                    'student_name': student_name,
                    'course_name': course_name,
                    'business': 'OncoOne'
                }
            )
            
            return {
                'success': True,
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id,
                'amount': amount_cad,
                'currency': 'CAD'
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def confirm_payment_intent(payment_intent_id, payment_method_id):
        """
        Confirm a payment intent with a payment method
        Returns: confirmed payment intent
        """
        try:
            payment_intent = stripe.PaymentIntent.confirm(
                payment_intent_id,
                payment_method=payment_method_id,
                return_url=os.getenv('STRIPE_RETURN_URL', 'https://oncoesthetics.ca/payment/success/')
            )
            
            return {
                'success': True,
                'status': payment_intent.status,
                'charges': payment_intent.charges.data,
                'payment_intent': payment_intent
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_payment_intent(payment_intent_id):
        """Retrieve a payment intent by ID"""
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                'success': True,
                'status': payment_intent.status,
                'charges': payment_intent.charges.data,
                'payment_intent': payment_intent
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def create_customer(email, name):
        """Create or retrieve a Stripe customer"""
        try:
            # Try to find existing customer
            customers = stripe.Customer.list(email=email, limit=1)
            
            if customers.data:
                return {
                    'success': True,
                    'customer_id': customers.data[0].id
                }
            
            # Create new customer
            customer = stripe.Customer.create(
                email=email,
                name=name,
                description=f"OncoOne Student: {name}"
            )
            
            return {
                'success': True,
                'customer_id': customer.id
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def process_payment_method_token(token):
        """Process a payment method token from Stripe.js"""
        try:
            # This validates the token exists in Stripe
            payment_method = stripe.PaymentMethod.retrieve(token)
            
            return {
                'success': True,
                'payment_method_id': payment_method.id,
                'card_brand': payment_method.card.brand if hasattr(payment_method, 'card') else 'unknown',
                'last_four': payment_method.card.last4 if hasattr(payment_method, 'card') else '0000'
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def refund_payment(charge_id, amount_cents=None):
        """Refund a charge (partial or full)"""
        try:
            refund_params = {'charge': charge_id}
            if amount_cents:
                refund_params['amount'] = amount_cents
            
            refund = stripe.Refund.create(**refund_params)
            
            return {
                'success': True,
                'refund_id': refund.id,
                'status': refund.status
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def verify_webhook_signature(payload, signature, webhook_secret):
        """Verify Stripe webhook signature for security"""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            return {
                'success': True,
                'event': event
            }
        except ValueError:
            return {
                'success': False,
                'error': 'Invalid payload'
            }
        except stripe.error.SignatureVerificationError:
            return {
                'success': False,
                'error': 'Invalid signature'
            }
