# 💳 OncoOne Education - Secure Payment System
## Production-Ready Stripe Integration with OTP Verification

---

## 🎯 Overview

Professional, secure payment processing system for OncoOne Education course enrollments with:

✅ **Stripe Payment Integration** - Industry-standard payment processing  
✅ **CVC/CVV Security** - Mandatory card verification code validation  
✅ **OTP Verification** - Two-factor authentication for payments  
✅ **Rate Limiting** - Protection against brute force attacks  
✅ **Comprehensive Logging** - Full audit trail of all transactions  
✅ **PDF Invoicing** - Automated invoice generation  
✅ **Email Notifications** - Professional email templates  
✅ **PCI Compliance** - Card data never touches your server  
✅ **Tax Calculation** - Canadian GST/HST support  

---

## 🔧 System Requirements

- Python 3.8+
- Django 4.2+
- PostgreSQL (recommended for production)
- Stripe Account (Live mode for production)
- SMTP Email Service
- SSL Certificate (HTTPS required)

---

## 📦 Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

**Key packages installed:**
- `stripe>=7.0.0` - Stripe Python SDK
- `django-ratelimit>=4.1.0` - Rate limiting for security
- `reportlab>=4.0.0` - PDF invoice generation

### 2. Environment Setup
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 3. Database Migration
```bash
# Run migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
```

### 4. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

---

## 🔐 Stripe Configuration

### Test Mode (Development)
1. Sign up at https://stripe.com
2. Get test API keys from Dashboard → Developers → API keys
3. Add to `.env`:
```env
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

### Live Mode (Production)
1. Complete Stripe account verification
2. Switch to "Live mode" in Stripe Dashboard
3. Get live API keys
4. Update `.env`:
```env
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### Webhook Setup
1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://yourdomain.com/api/payment/stripe-webhook/`
3. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `charge.refunded`

---

## 💳 Payment Flow

### 1. Student Registration
- Student registers for course(s)
- System creates Registration and Enrollment records

### 2. Payment Portal
- Student enters email to access payment portal
- System validates student and enrolled courses

### 3. Payment Amount
- Student selects course to pay for
- Can make partial or full payment
- Tax calculated automatically (GST/HST)

### 4. Card Entry (with CVC)
**Security Features:**
- ✅ Card number validation (Luhn algorithm)
- ✅ Expiry date validation
- ✅ **CVC/CVV code required** (3-4 digits)
- ✅ Postal code validation
- ✅ Cardholder name validation

**Supported Cards:**
- Visa
- Mastercard
- American Express
- Discover
- Diners Club
- JCB
- UnionPay

### 5. OTP Verification
- 6-digit OTP sent to student email
- Valid for 10 minutes (configurable)
- Maximum 3 verification attempts
- Rate limiting prevents abuse
- IP tracking for security

### 6. Payment Processing
- Stripe Payment Intent created
- Card charged securely via Stripe
- Transaction logged comprehensively

### 7. Confirmation
- PDF invoice generated automatically
- Confirmation email with invoice attached
- Payment record updated in database

---

## 🔒 Security Features

### Card Security
- **CVC Required**: Must enter 3-4 digit security code
- **No Storage**: Card data processed by Stripe, never stored on server
- **Encryption**: All card data encrypted in transit (TLS 1.2+)
- **Tokenization**: Stripe tokenizes card data

### OTP Security
- **6-Digit Codes**: Securely generated random OTP
- **Time-Limited**: Expires after 10 minutes
- **Attempt Limiting**: Max 3 attempts per OTP
- **Rate Limiting**: Prevents brute force attacks
- **Lockout**: Temporary lockout after repeated failures
- **IP Tracking**: Security audit trail

### Application Security
- **CSRF Protection**: All forms protected
- **SQL Injection**: Django ORM prevents attacks
- **XSS Protection**: Input sanitization
- **HTTPS Only**: Production requires SSL
- **Session Security**: Secure cookie settings

### PCI Compliance
✅ **Level 1 PCI DSS Compliance** via Stripe integration
- Card data never touches your server
- Stripe.js handles sensitive data
- No card data in logs or database
- Only last 4 digits stored

---

## 📧 Email Templates

Professional email templates for:
1. **OTP Verification** - Payment authorization code
2. **Payment Confirmation** - Success notification with invoice
3. **Payment Failed** - Error notification with retry instructions
4. **Admin Notifications** - New payment alerts

### Customization
Edit in `core/views.py` or create template files in `templates/emails/`

---

## 📊 Payment Testing

### Test Cards (Stripe Test Mode)

**Successful Payment:**
```
Card: 4242 4242 4242 4242
Expiry: Any future date
CVC: Any 3 digits
Postal: Any valid code
```

**Declined Card:**
```
Card: 4000 0000 0000 0002
Expiry: Any future date
CVC: Any 3 digits
```

**Requires Authentication:**
```
Card: 4000 0025 0000 3155
Expiry: Any future date
CVC: Any 3 digits
```

**Insufficient Funds:**
```
Card: 4000 0000 0000 9995
```

### Testing Checklist
- [ ] Successful payment with valid card
- [ ] Declined card handling
- [ ] Invalid CVC error
- [ ] Expired card error
- [ ] OTP email delivery
- [ ] OTP verification (correct code)
- [ ] OTP max attempts (3 failures)
- [ ] OTP expiry (after 10 min)
- [ ] Invoice generation
- [ ] PDF invoice download
- [ ] Confirmation email

---

## 🎛️ Configuration Variables

### Payment Limits
```env
MIN_PAYMENT_AMOUNT=10.00      # Minimum payment in CAD
MAX_PAYMENT_AMOUNT=10000.00   # Maximum payment in CAD
PAYMENT_TIMEOUT_MINUTES=30    # Payment session timeout
```

### OTP Settings
```env
OTP_EXPIRY_MINUTES=10         # OTP validity period
OTP_MAX_ATTEMPTS=3            # Maximum verification attempts
OTP_LENGTH=6                  # OTP code length
```

### Tax Configuration
```env
TAX_RATE=0.05                 # 5% GST (adjust for province)
TAX_NAME=GST                  # Tax label
```

### Business Information
```env
BUSINESS_NAME=OncoOne Education
BUSINESS_EMAIL=info@oncoesthetics.ca
BUSINESS_PHONE=+1-XXX-XXX-XXXX
BUSINESS_ADDRESS=Your Address, Canada
```

---

## 📁 File Structure

```
core/
├── models.py                 # Payment, OTP, Invoice models
├── views.py                  # Payment view functions
├── stripe_processor.py       # Stripe API integration
├── payment_security.py       # OTP & security managers
├── urls.py                   # Payment URL routes
└── migrations/
    └── 0008_enhance_otp_security.py

templates/payments/
├── payment_card_form_stripe.html    # Card entry with CVC
├── payment_otp_verification.html    # OTP verification
├── payment_success.html             # Payment confirmation
└── payment_summary.html             # Payment summary

logs/
├── payment.log               # Payment transactions
└── security.log              # Security events

media/
└── invoices/                 # Generated PDF invoices
```

---

## 🔍 Monitoring & Logs

### Payment Logs
Location: `logs/payment.log`

Tracks:
- Payment Intent creation
- Stripe API calls
- Transaction success/failure
- Invoice generation
- Email delivery

### Security Logs
Location: `logs/security.log`

Tracks:
- OTP generation
- OTP verification attempts
- Failed login attempts
- Rate limiting events
- IP address tracking

### Stripe Dashboard
Monitor in real-time:
- https://dashboard.stripe.com/payments
- Failed payments
- Disputes/chargebacks
- Refunds

---

## 🔄 Refund Process

### From Admin Panel
1. Login to admin: `/admin/`
2. Navigate to Payments
3. Select payment to refund
4. Click "Refund" action
5. Confirm refund amount

### Programmatically
```python
from core.stripe_processor import StripePaymentProcessor

result = StripePaymentProcessor.refund_payment(
    charge_id='ch_xxx',
    amount_cents=1000,  # $10.00 (optional, omit for full refund)
    reason='requested_by_customer'
)
```

---

## 🆘 Troubleshooting

### Payment Fails with "Invalid API Key"
✅ Verify `STRIPE_SECRET_KEY` in `.env` matches Stripe Dashboard  
✅ Ensure using correct mode (test vs live)  
✅ Check for spaces/extra characters in key

### OTP Email Not Received
✅ Check spam/junk folder  
✅ Verify SMTP settings in `.env`  
✅ Check `logs/payment.log` for email errors  
✅ Test with Gmail app password

### CVC Not Being Validated
✅ Ensure Stripe Elements mounted correctly  
✅ Check browser console for JavaScript errors  
✅ Verify `cardComplete` variable is tracking status  
✅ Check `stripe.createPaymentMethod()` response

### Webhook Not Working
✅ Verify endpoint is publicly accessible (HTTPS)  
✅ Check webhook signing secret in `.env`  
✅ Review Stripe Dashboard → Webhooks → Event Log  
✅ Ensure endpoint returns 200 status code

---

## 🎓 Best Practices

### Security
1. ✅ Always use HTTPS in production
2. ✅ Never log full card numbers or CVC
3. ✅ Rotate API keys periodically
4. ✅ Monitor Stripe Dashboard daily
5. ✅ Keep Django and dependencies updated

### Performance
1. ✅ Use PostgreSQL for production
2. ✅ Enable database connection pooling
3. ✅ Cache static files with CDN
4. ✅ Monitor database query performance

### User Experience
1. ✅ Clear error messages
2. ✅ Loading indicators during processing
3. ✅ Mobile-responsive design
4. ✅ Email confirmations
5. ✅ Professional invoice design

---

## 📞 Support

### Stripe Support
- Documentation: https://stripe.com/docs
- Support: support@stripe.com
- Phone: Available in Stripe Dashboard

### Django Documentation
- https://docs.djangoproject.com

---

## 📝 License

Proprietary - OncoOne Education  
All rights reserved.

---

## ✨ Updates & Changelog

### Version 2.0 (January 2026)
- ✅ Enhanced CVC validation and enforcement
- ✅ Professional OTP security with rate limiting
- ✅ Comprehensive logging system
- ✅ Production-ready Stripe integration
- ✅ Improved error handling
- ✅ Professional email templates
- ✅ Security audit and hardening

---

**Ready for Production! 🚀**

For deployment instructions, see `PRODUCTION_DEPLOYMENT_CHECKLIST.md`
