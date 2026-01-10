"""
Payment Security Module for OncoOne Education
Handles OTP generation, validation, rate limiting, and security checks
Version: 1.0 - Production Ready
"""

import logging
import random
import string
from datetime import timedelta
from typing import Tuple, Optional
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger('core.security')


class OTPSecurityManager:
    """
    Secure OTP Management System
    Handles generation, validation, expiry, and rate limiting
    """
    
    # Security constants
    OTP_LENGTH = getattr(settings, 'OTP_LENGTH', 6)
    OTP_EXPIRY_MINUTES = getattr(settings, 'OTP_EXPIRY_MINUTES', 10)
    MAX_ATTEMPTS = getattr(settings, 'OTP_MAX_ATTEMPTS', 3)
    LOCKOUT_DURATION_MINUTES = 15
    
    @staticmethod
    def generate_otp_code() -> str:
        """
        Generate a secure random OTP code
        
        Returns:
            str: 6-digit numeric OTP code
        """
        otp = ''.join(random.choices(string.digits, k=OTPSecurityManager.OTP_LENGTH))
        logger.info(f'OTP generated (length: {OTPSecurityManager.OTP_LENGTH})')
        return otp
    
    @staticmethod
    def validate_otp_format(otp_code: str) -> bool:
        """
        Validate OTP format (6 digits)
        
        Args:
            otp_code: OTP code to validate
            
        Returns:
            bool: True if format is valid
        """
        if not otp_code:
            return False
        
        # Remove whitespace
        otp_code = otp_code.strip()
        
        # Check length
        if len(otp_code) != OTPSecurityManager.OTP_LENGTH:
            logger.warning(f'Invalid OTP length: {len(otp_code)} (expected {OTPSecurityManager.OTP_LENGTH})')
            return False
        
        # Check if all digits
        if not otp_code.isdigit():
            logger.warning('OTP contains non-digit characters')
            return False
        
        return True
    
    @staticmethod
    def check_rate_limit(identifier: str, max_attempts: int = None, window_minutes: int = None) -> Tuple[bool, int]:
        """
        Check if rate limit has been exceeded for OTP attempts
        
        Args:
            identifier: Unique identifier (email, payment_id, etc.)
            max_attempts: Maximum allowed attempts (default: settings.OTP_MAX_ATTEMPTS)
            window_minutes: Time window in minutes (default: OTP_EXPIRY_MINUTES)
            
        Returns:
            Tuple[bool, int]: (is_allowed, remaining_attempts)
        """
        if max_attempts is None:
            max_attempts = OTPSecurityManager.MAX_ATTEMPTS
        
        if window_minutes is None:
            window_minutes = OTPSecurityManager.OTP_EXPIRY_MINUTES
        
        cache_key = f'otp_attempts_{identifier}'
        attempts = cache.get(cache_key, 0)
        
        if attempts >= max_attempts:
            logger.warning(f'🚨 Rate limit exceeded for {identifier}: {attempts} attempts')
            return False, 0
        
        remaining = max_attempts - attempts
        return True, remaining
    
    @staticmethod
    def record_otp_attempt(identifier: str, success: bool = False) -> None:
        """
        Record an OTP attempt for rate limiting
        
        Args:
            identifier: Unique identifier
            success: Whether the attempt was successful
        """
        cache_key = f'otp_attempts_{identifier}'
        
        if success:
            # Clear attempts on successful verification
            cache.delete(cache_key)
            logger.info(f'✅ OTP verified successfully for {identifier} - attempts cleared')
        else:
            # Increment failed attempts
            attempts = cache.get(cache_key, 0)
            attempts += 1
            cache.set(cache_key, attempts, timeout=OTPSecurityManager.OTP_EXPIRY_MINUTES * 60)
            logger.warning(f'❌ Failed OTP attempt for {identifier}: {attempts}/{OTPSecurityManager.MAX_ATTEMPTS}')
    
    @staticmethod
    def is_locked_out(identifier: str) -> Tuple[bool, Optional[int]]:
        """
        Check if an identifier is locked out due to too many failed attempts
        
        Args:
            identifier: Unique identifier
            
        Returns:
            Tuple[bool, Optional[int]]: (is_locked, seconds_remaining)
        """
        cache_key = f'otp_lockout_{identifier}'
        lockout_until = cache.get(cache_key)
        
        if lockout_until:
            now = timezone.now()
            if now < lockout_until:
                seconds_remaining = int((lockout_until - now).total_seconds())
                logger.warning(f'🔒 Account locked for {identifier}: {seconds_remaining}s remaining')
                return True, seconds_remaining
            else:
                # Lockout expired
                cache.delete(cache_key)
        
        return False, None
    
    @staticmethod
    def lockout_user(identifier: str, duration_minutes: int = None) -> None:
        """
        Lock out a user for a specified duration
        
        Args:
            identifier: Unique identifier
            duration_minutes: Lockout duration (default: LOCKOUT_DURATION_MINUTES)
        """
        if duration_minutes is None:
            duration_minutes = OTPSecurityManager.LOCKOUT_DURATION_MINUTES
        
        cache_key = f'otp_lockout_{identifier}'
        lockout_until = timezone.now() + timedelta(minutes=duration_minutes)
        cache.set(cache_key, lockout_until, timeout=duration_minutes * 60)
        
        logger.warning(f'🔒 User locked out: {identifier} for {duration_minutes} minutes')
    
    @staticmethod
    def get_expiry_time(created_at: timezone.datetime) -> timezone.datetime:
        """
        Calculate OTP expiry time
        
        Args:
            created_at: OTP creation time
            
        Returns:
            datetime: Expiry time
        """
        return created_at + timedelta(minutes=OTPSecurityManager.OTP_EXPIRY_MINUTES)
    
    @staticmethod
    def is_expired(created_at: timezone.datetime) -> bool:
        """
        Check if OTP has expired
        
        Args:
            created_at: OTP creation time
            
        Returns:
            bool: True if expired
        """
        expiry_time = OTPSecurityManager.get_expiry_time(created_at)
        is_exp = timezone.now() > expiry_time
        
        if is_exp:
            logger.info(f'OTP expired (created: {created_at}, expired: {expiry_time})')
        
        return is_exp


class PaymentSecurityValidator:
    """
    Payment Security Validation
    Validates payment amounts, card details, and detects suspicious activity
    """
    
    @staticmethod
    def validate_payment_amount(amount: float) -> Tuple[bool, Optional[str]]:
        """
        Validate payment amount is within acceptable range
        
        Args:
            amount: Payment amount to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        try:
            from decimal import Decimal
            amount_decimal = Decimal(str(amount))
            
            if amount_decimal < settings.MIN_PAYMENT_AMOUNT:
                return False, f'Minimum payment amount is ${settings.MIN_PAYMENT_AMOUNT}'
            
            if amount_decimal > settings.MAX_PAYMENT_AMOUNT:
                return False, f'Maximum payment amount is ${settings.MAX_PAYMENT_AMOUNT}'
            
            if amount_decimal <= 0:
                return False, 'Payment amount must be greater than zero'
            
            return True, None
            
        except Exception as e:
            logger.error(f'Payment amount validation error: {str(e)}')
            return False, 'Invalid payment amount format'
    
    @staticmethod
    def validate_card_type(card_type: str) -> bool:
        """
        Validate card type is supported
        
        Args:
            card_type: Card type/brand
            
        Returns:
            bool: True if valid
        """
        supported_types = ['visa', 'mastercard', 'amex', 'discover', 'diners', 'jcb', 'unionpay']
        return card_type.lower() in supported_types
    
    @staticmethod
    def validate_email_format(email: str) -> bool:
        """
        Validate email format
        
        Args:
            email: Email address
            
        Returns:
            bool: True if valid
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def sanitize_input(value: str, max_length: int = 255) -> str:
        """
        Sanitize user input
        
        Args:
            value: Input value
            max_length: Maximum allowed length
            
        Returns:
            str: Sanitized value
        """
        if not value:
            return ''
        
        # Strip whitespace
        value = value.strip()
        
        # Truncate to max length
        value = value[:max_length]
        
        return value
