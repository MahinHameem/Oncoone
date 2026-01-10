"""
Stripe Payment Processing Module for OncoOne Education
Handles secure payment processing with comprehensive error handling and logging
Version: 2.0 - Production Ready
Author: OncoOne Development Team
Last Updated: January 2026
"""

import stripe
import os
import logging
from decimal import Decimal
from typing import Dict, Optional, Any
from django.conf import settings

# Initialize logging
logger = logging.getLogger('core.payment')

# Initialize Stripe with API key
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', settings.STRIPE_SECRET_KEY)


class PaymentProcessingError(Exception):
    """Custom exception for payment processing errors"""
    pass


class StripePaymentProcessor:
    """
    Professional Stripe Payment Processor for OncoOne Education
    Handles all payment operations with comprehensive error handling and security
    """
    
    # Class constants
    SUPPORTED_CURRENCIES = ['cad', 'usd', 'eur', 'gbp']
    MIN_AMOUNT_CENTS = 50  # $0.50 minimum (Stripe requirement)
    
    @staticmethod
    def validate_amount(amount_cad: Decimal) -> bool:
        """
        Validate payment amount meets business and Stripe requirements
        
        Args:
            amount_cad: Payment amount in CAD
            
        Returns:
            bool: True if valid
            
        Raises:
            PaymentProcessingError: If amount is invalid
        """
        try:
            amount_decimal = Decimal(str(amount_cad))
            
            if amount_decimal < settings.MIN_PAYMENT_AMOUNT:
                raise PaymentProcessingError(
                    f'Payment amount must be at least ${settings.MIN_PAYMENT_AMOUNT}'
                )
            
            if amount_decimal > settings.MAX_PAYMENT_AMOUNT:
                raise PaymentProcessingError(
                    f'Payment amount cannot exceed ${settings.MAX_PAYMENT_AMOUNT}'
                )
            
            return True
            
        except (ValueError, TypeError) as e:
            logger.error(f'Invalid amount format: {amount_cad} - {str(e)}')
            raise PaymentProcessingError('Invalid payment amount format')
    
    @staticmethod
    def get_stripe_amount(amount_cad: Decimal) -> int:
        """
        Convert CAD amount to cents for Stripe API
        
        Args:
            amount_cad: Amount in Canadian dollars
            
        Returns:
            int: Amount in cents
            
        Raises:
            PaymentProcessingError: If conversion fails
        """
        try:
            cents = int(float(amount_cad) * 100)
            
            if cents < StripePaymentProcessor.MIN_AMOUNT_CENTS:
                raise PaymentProcessingError(
                    f'Amount too small. Minimum is ${StripePaymentProcessor.MIN_AMOUNT_CENTS / 100:.2f}'
                )
            
            return cents
            
        except (ValueError, TypeError) as e:
            logger.error(f'Amount conversion failed: {amount_cad} - {str(e)}')
            raise PaymentProcessingError('Invalid payment amount')
    
    @staticmethod
    def create_payment_intent(
        amount_cad: Decimal,
        email: str,
        student_name: str,
        course_name: str,
        payment_id: Optional[str] = None,
        payment_method_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a Stripe Payment Intent for secure payment processing
        
        Args:
            amount_cad: Payment amount in CAD
            email: Student email address
            student_name: Full name of student
            course_name: Name of course being purchased
            payment_id: Internal payment record ID (optional)
            
        Returns:
            Dict with success status and payment intent details or error
        """
        try:
            # Validate amount before processing
            StripePaymentProcessor.validate_amount(amount_cad)
            amount_cents = StripePaymentProcessor.get_stripe_amount(amount_cad)
            
            # Prepare metadata (Stripe limits: 500 chars per value, 50 keys max)
            metadata = {
                'student_name': str(student_name)[:500],
                'student_email': str(email)[:500],
                'course_name': str(course_name)[:500],
                'business': settings.BUSINESS_NAME,
            }
            
            if payment_id:
                metadata['payment_id'] = str(payment_id)
            if payment_method_id:
                metadata['payment_method_id'] = str(payment_method_id)
            
            # Create Payment Intent with Stripe
            # Attach payment method so we can confirm after OTP
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=settings.STRIPE_CURRENCY,
                description=f'{settings.BUSINESS_NAME} - {course_name}',
                statement_descriptor_suffix=settings.STRIPE_STATEMENT_DESCRIPTOR[:22],  # Max 22 chars for suffix
                receipt_email=email,
                metadata=metadata,
                payment_method_types=['card'],
                payment_method=payment_method_id,
                confirmation_method='automatic',
                confirm=False,
                payment_method_options={
                    'card': {
                        'request_three_d_secure': 'automatic'
                    }
                },
            )
            
            logger.info(
                f'✅ Payment Intent created: {payment_intent.id} | '
                f'Student: {email} | Amount: ${amount_cad} CAD | Course: {course_name}'
            )
            
            return {
                'success': True,
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id,
                'amount': amount_cad,
                'currency': 'CAD',
                'status': payment_intent.status
            }
            
        except PaymentProcessingError as e:
            logger.warning(f'Payment validation error: {str(e)}')
            return {
                'success': False,
                'error': str(e),
                'error_type': 'validation_error'
            }
            
        except stripe.error.CardError as e:
            logger.warning(f'Card declined: {e.user_message} | Code: {e.code}')
            return {
                'success': False,
                'error': 'Your card was declined. Please try a different payment method.',
                'error_code': e.code,
                'error_type': 'card_error'
            }
            
        except stripe.error.RateLimitError as e:
            logger.error(f'Stripe rate limit exceeded: {str(e)}')
            return {
                'success': False,
                'error': 'Too many requests. Please wait a moment and try again.',
                'error_type': 'rate_limit_error'
            }
            
        except stripe.error.InvalidRequestError as e:
            logger.error(f'Invalid Stripe request: {str(e)}')
            return {
                'success': False,
                'error': 'Invalid payment request. Please contact support.',
                'error_type': 'invalid_request_error'
            }
            
        except stripe.error.AuthenticationError as e:
            logger.critical(f'🚨 Stripe authentication failed: {str(e)}')
            return {
                'success': False,
                'error': 'Payment system configuration error. Please contact support immediately.',
                'error_type': 'authentication_error'
            }
            
        except stripe.error.APIConnectionError as e:
            logger.error(f'Stripe connection failed: {str(e)}')
            return {
                'success': False,
                'error': 'Unable to connect to payment processor. Please check your internet connection and try again.',
                'error_type': 'connection_error'
            }
            
        except stripe.error.StripeError as e:
            logger.error(f'Stripe error: {str(e)}')
            return {
                'success': False,
                'error': 'Payment processing error. Please try again or contact support.',
                'error_type': 'stripe_error'
            }
            
        except Exception as e:
            logger.critical(f'🚨 Unexpected payment error: {str(e)}', exc_info=True)
            return {
                'success': False,
                'error': 'An unexpected error occurred. Please contact support.',
                'error_type': 'unexpected_error'
            }
    
    @staticmethod
    def retrieve_payment_intent(payment_intent_id: str) -> Dict[str, Any]:
        """
        Retrieve and verify a payment intent from Stripe
        
        Args:
            payment_intent_id: Stripe Payment Intent ID
            
        Returns:
            Dict with payment intent details or error
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(
                payment_intent_id,
                expand=['charges', 'latest_charge', 'payment_method']
            )
            
            logger.info(f'Payment Intent retrieved: {payment_intent_id} | Status: {payment_intent.status}')
            
            charges_list = []
            try:
                if hasattr(payment_intent, 'charges') and payment_intent.charges is not None:
                    data = getattr(payment_intent.charges, 'data', None)
                    if data:
                        charges_list = data
            except Exception:
                charges_list = []

            return {
                'success': True,
                'status': payment_intent.status,
                'amount': payment_intent.amount / 100,
                'currency': payment_intent.currency.upper(),
                'charges': charges_list,
                'payment_intent': payment_intent
            }
            
        except stripe.error.StripeError as e:
            logger.error(f'Error retrieving payment intent {payment_intent_id}: {str(e)}')
            return {
                'success': False,
                'error': 'Unable to retrieve payment information.',
                'error_type': 'retrieval_error'
            }
    
    @staticmethod
    def confirm_payment(payment_intent_id: str, payment_method_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Confirm a payment intent and return latest status/details
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(
                payment_intent_id,
                expand=['charges', 'latest_charge', 'payment_method']
            )

            # If not succeeded, attempt to confirm with attached payment method
            if payment_intent.status != 'succeeded':
                try:
                    confirm_kwargs = {}
                    if payment_method_id:
                        confirm_kwargs['payment_method'] = payment_method_id
                    payment_intent = stripe.PaymentIntent.confirm(payment_intent_id, **confirm_kwargs)
                except stripe.error.StripeError as e:
                    logger.error(f'Error confirming payment {payment_intent_id}: {str(e)}')
                    return {
                        'success': False,
                        'status': payment_intent.status,
                        'error': f'Confirmation failed: {str(e)}',
                        'error_type': 'confirmation_error'
                    }

            if payment_intent.status == 'succeeded':
                logger.info(f'✅ Payment confirmed successfully: {payment_intent_id}')

                # Safely extract charges; fallback to latest_charge when not expanded
                charges_list = []
                charge_id = None
                try:
                    if hasattr(payment_intent, 'charges') and payment_intent.charges is not None:
                        data = getattr(payment_intent.charges, 'data', None)
                        if data:
                            charges_list = data
                            try:
                                charge_id = charges_list[0].id
                            except Exception:
                                charge_id = None
                    # Fallback: use latest_charge if available
                    if not charge_id and getattr(payment_intent, 'latest_charge', None):
                        charge_id = payment_intent.latest_charge
                except Exception as ex:
                    logger.warning(f"Unable to extract charges for {payment_intent_id}: {ex}")

                return {
                    'success': True,
                    'status': 'succeeded',
                    'amount': payment_intent.amount / 100,
                    'charges': charges_list,
                    'charge_id': charge_id,
                    'payment_method': payment_intent.payment_method
                }
            else:
                logger.warning(
                    f'⚠️  Payment not succeeded: {payment_intent_id} | '
                    f'Status: {payment_intent.status}'
                )
                return {
                    'success': False,
                    'status': payment_intent.status,
                    'requires_action': payment_intent.status == 'requires_action',
                    'client_secret': payment_intent.client_secret,
                    'error': f'Payment status: {payment_intent.status.replace("_", " ").title()}'
                }

        except stripe.error.StripeError as e:
            logger.error(f'Error retrieving payment {payment_intent_id}: {str(e)}')
            return {
                'success': False,
                'error': 'Unable to confirm payment status.',
                'error_type': 'confirmation_error'
            }
    
    @staticmethod
    def create_customer(email: str, name: str) -> Dict[str, Any]:
        """
        Create or retrieve a Stripe customer account
        
        Args:
            email: Customer email address
            name: Customer full name
            
        Returns:
            Dict with customer ID and creation status
        """
        try:
            # Search for existing customer by email
            customers = stripe.Customer.list(email=email, limit=1)
            
            if customers.data:
                logger.info(f'Existing Stripe customer found: {email}')
                return {
                    'success': True,
                    'customer_id': customers.data[0].id,
                    'is_new': False
                }
            
            # Create new customer
            customer = stripe.Customer.create(
                email=email,
                name=name,
                description=f'{settings.BUSINESS_NAME} Student - {name}'
            )
            
            logger.info(f'✅ New Stripe customer created: {customer.id} for {email}')
            return {
                'success': True,
                'customer_id': customer.id,
                'is_new': True
            }
            
        except stripe.error.StripeError as e:
            logger.error(f'Error creating/retrieving customer for {email}: {str(e)}')
            return {
                'success': False,
                'error': 'Unable to create customer account.',
                'error_type': 'customer_error'
            }
    
    @staticmethod
    def refund_payment(
        charge_id: str,
        amount_cents: Optional[int] = None,
        reason: str = 'requested_by_customer'
    ) -> Dict[str, Any]:
        """
        Process a refund for a completed payment (full or partial)
        
        Args:
            charge_id: Stripe Charge ID to refund
            amount_cents: Amount to refund in cents (None for full refund)
            reason: Reason for refund (requested_by_customer, duplicate, fraudulent)
            
        Returns:
            Dict with refund status and details
        """
        try:
            refund_params = {
                'charge': charge_id,
                'reason': reason
            }
            
            if amount_cents:
                refund_params['amount'] = amount_cents
            
            refund = stripe.Refund.create(**refund_params)
            
            logger.info(
                f'✅ Refund processed: {refund.id} for charge {charge_id} | '
                f'Amount: ${refund.amount / 100:.2f} {refund.currency.upper()} | '
                f'Reason: {reason}'
            )
            
            return {
                'success': True,
                'refund_id': refund.id,
                'status': refund.status,
                'amount': refund.amount / 100,
                'currency': refund.currency.upper()
            }
            
        except stripe.error.StripeError as e:
            logger.error(f'Refund failed for charge {charge_id}: {str(e)}')
            return {
                'success': False,
                'error': 'Unable to process refund. Please contact support.',
                'error_type': 'refund_error'
            }
    
    @staticmethod
    def verify_webhook_signature(
        payload: bytes,
        signature: str
    ) -> Dict[str, Any]:
        """
        Verify Stripe webhook signature for security and authenticity
        
        Args:
            payload: Raw request body (bytes)
            signature: Stripe-Signature header value
            
        Returns:
            Dict with verification result and event data
        """
        try:
            webhook_secret = settings.STRIPE_WEBHOOK_SECRET
            
            if not webhook_secret:
                logger.warning('⚠️  Webhook secret not configured - skipping verification')
                return {
                    'success': False,
                    'error': 'Webhook verification not configured'
                }
            
            # Verify signature and construct event
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            
            logger.info(f'✅ Webhook verified: {event.type} | ID: {event.id}')
            return {
                'success': True,
                'event': event,
                'event_type': event.type
            }
            
        except ValueError as e:
            logger.error(f'Invalid webhook payload: {str(e)}')
            return {
                'success': False,
                'error': 'Invalid payload'
            }
            
        except stripe.error.SignatureVerificationError as e:
            logger.error(f'🚨 Invalid webhook signature - possible security threat: {str(e)}')
            return {
                'success': False,
                'error': 'Invalid signature'
            }
    
    @staticmethod
    def get_charge_details(charge_id: str) -> Dict[str, Any]:
        """
        Retrieve details of a specific charge
        
        Args:
            charge_id: Stripe Charge ID
            
        Returns:
            Dict with charge details
        """
        try:
            charge = stripe.Charge.retrieve(charge_id)
            
            return {
                'success': True,
                'charge_id': charge.id,
                'amount': charge.amount / 100,
                'currency': charge.currency.upper(),
                'status': charge.status,
                'receipt_url': charge.receipt_url,
                'payment_method': charge.payment_method_details.type if charge.payment_method_details else None
            }
            
        except stripe.error.StripeError as e:
            logger.error(f'Error retrieving charge {charge_id}: {str(e)}')
            return {
                'success': False,
                'error': 'Unable to retrieve charge details.'
            }

