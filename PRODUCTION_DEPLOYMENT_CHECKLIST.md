# 🚀 PRODUCTION DEPLOYMENT CHECKLIST
## OncoOne Education Payment System - Go-Live Guide

---

## ✅ PRE-DEPLOYMENT CHECKLIST

### 1. Environment Configuration
- [ ] Copy `.env.example` to `.env`
- [ ] Update `DJANGO_SECRET_KEY` with a strong random key
- [ ] Set `DJANGO_DEBUG=False`
- [ ] Configure `DJANGO_ALLOWED_HOSTS` with your domain
- [ ] Set up CSRF_TRUSTED_ORIGINS with your HTTPS domains

### 2. Stripe Configuration (CRITICAL)
- [ ] Create Stripe account at https://stripe.com
- [ ] Complete business verification in Stripe Dashboard
- [ ] Get **LIVE** API keys from https://dashboard.stripe.com/apikeys
- [ ] Add `STRIPE_PUBLIC_KEY=pk_live_...` to .env
- [ ] Add `STRIPE_SECRET_KEY=sk_live_...` to .env
- [ ] Set up webhooks at https://dashboard.stripe.com/webhooks
- [ ] Add webhook endpoint: `https://yourdomain.com/api/payment/stripe-webhook/`
- [ ] Copy webhook signing secret to `STRIPE_WEBHOOK_SECRET`
- [ ] Enable required webhook events:
  - `payment_intent.succeeded`
  - `payment_intent.payment_failed`
  - `charge.refunded`

### 3. Database Setup
- [ ] Set up PostgreSQL database (recommended for production)
- [ ] Update database credentials in .env
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`

### 4. Email Configuration
- [ ] Configure SMTP settings in .env
- [ ] Test email delivery
- [ ] Set up SPF, DKIM, DMARC records for your domain
- [ ] Verify sender email addresses

### 5. Security Settings
- [ ] Enable HTTPS/SSL on your server
- [ ] Configure firewall rules
- [ ] Set up regular database backups
- [ ] Review and update payment limits (MIN/MAX amounts)
- [ ] Configure tax rates for your province

### 6. Payment Testing
- [ ] Test with Stripe test cards FIRST:
  - Success: 4242 4242 4242 4242
  - Declined: 4000 0000 0000 0002
  - Requires authentication: 4000 0025 0000 3155
- [ ] Test OTP email delivery
- [ ] Verify invoice generation
- [ ] Test refund process
- [ ] Verify webhook handling

---

## 🔧 INSTALLATION & DEPENDENCIES

### Install Required Packages
```bash
pip install -r requirements.txt
```

### Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Create Logs Directory
```bash
mkdir logs
```

---

## 📋 CRITICAL STRIPE SETUP STEPS

### Step 1: Activate Your Stripe Account
1. Go to https://dashboard.stripe.com
2. Complete business verification
3. Provide business details, tax ID, banking information
4. Wait for account activation (usually 1-3 business days)

### Step 2: Get Live API Keys
1. Switch to "Live mode" (toggle in Stripe Dashboard)
2. Navigate to Developers → API keys
3. Copy your **Publishable key** (starts with `pk_live_`)
4. Copy your **Secret key** (starts with `sk_live_`)
5. **NEVER** commit these keys to version control!

### Step 3: Configure Webhooks
1. Go to Developers → Webhooks
2. Click "Add endpoint"
3. Enter: `https://yourdomain.com/api/payment/stripe-webhook/`
4. Select events:
   - ✅ `payment_intent.succeeded`
   - ✅ `payment_intent.payment_failed`
   - ✅ `charge.refunded`
5. Copy the webhook signing secret (starts with `whsec_`)

### Step 4: Test Mode First!
Before going live:
- Use test API keys (pk_test_ and sk_test_)
- Test all payment flows
- Verify OTP and email delivery
- Check invoice generation
- Test refunds

---

## 🔐 SECURITY REQUIREMENTS

### SSL/HTTPS (REQUIRED)
- [ ] Install SSL certificate on your server
- [ ] Force HTTPS redirects
- [ ] Verify secure connection (green padlock in browser)

### PCI Compliance
- [ ] ✅ You are PCI compliant by using Stripe.js (card data never touches your server)
- [ ] Never log or store full card numbers
- [ ] Never log or store CVC codes
- [ ] Only store last 4 digits and card brand

### Django Security
- [ ] Set `SESSION_COOKIE_SECURE=True` (done automatically when DEBUG=False)
- [ ] Set `CSRF_COOKIE_SECURE=True` (done automatically when DEBUG=False)
- [ ] Keep `SECRET_KEY` secure and unique
- [ ] Regularly update Django and dependencies

---

## 📧 EMAIL TEMPLATE CUSTOMIZATION

### Update Business Information
Edit in `.env`:
- `BUSINESS_NAME` - Your company name
- `BUSINESS_EMAIL` - Support email
- `BUSINESS_PHONE` - Contact phone number
- `BUSINESS_ADDRESS` - Physical address

### Email Providers
Recommended SMTP providers:
- **SendGrid** - 100 emails/day free
- **Mailgun** - 5,000 emails/month free
- **Amazon SES** - Very reliable, pay-as-you-go
- **Gmail** - For testing only (limited sends per day)

---

## 💳 PAYMENT FLOW VERIFICATION

### Test Complete Payment Flow:
1. [ ] Student registration
2. [ ] Course selection
3. [ ] Payment amount entry
4. [ ] Card details entry (including CVC!)
5. [ ] OTP generation and email delivery
6. [ ] OTP verification (test max attempts)
7. [ ] Payment processing through Stripe
8. [ ] Invoice generation
9. [ ] Confirmation email with invoice PDF
10. [ ] Admin dashboard payment view

### Test Error Scenarios:
- [ ] Invalid card number
- [ ] Expired card
- [ ] Insufficient funds
- [ ] Wrong CVC
- [ ] Wrong OTP (3 failed attempts)
- [ ] Expired OTP
- [ ] Network timeout

---

## 📊 MONITORING & MAINTENANCE

### Stripe Dashboard Monitoring
- [ ] Set up daily/weekly payment reports
- [ ] Enable fraud detection alerts
- [ ] Monitor dispute/chargeback notifications
- [ ] Review failed payments

### Log Monitoring
Check these files regularly:
- `logs/payment.log` - Payment transactions
- `logs/security.log` - Security events, OTP attempts

### Database Backups
- [ ] Set up automated daily backups
- [ ] Test backup restoration process
- [ ] Store backups securely off-site

---

## 🚨 TROUBLESHOOTING

### Payment Not Working?
1. Check Stripe Dashboard for errors
2. Verify API keys are LIVE mode (pk_live_ and sk_live_)
3. Check logs/payment.log for errors
4. Ensure STRIPE_SECRET_KEY in .env matches Dashboard
5. Verify domain is HTTPS

### OTP Not Received?
1. Check email spam/junk folder
2. Verify SMTP settings in .env
3. Check logs for email sending errors
4. Test email with simple Django shell command

### Webhook Not Working?
1. Verify webhook URL is publicly accessible
2. Check webhook signing secret matches
3. Review Stripe Dashboard → Webhooks → Events
4. Ensure endpoint returns 200 status

---

## 📞 SUPPORT RESOURCES

### Stripe Support
- Dashboard: https://dashboard.stripe.com
- Documentation: https://stripe.com/docs
- Support: https://support.stripe.com

### Django Documentation
- Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/
- Security: https://docs.djangoproject.com/en/stable/topics/security/

---

## ✨ FINAL GO-LIVE CHECKLIST

Before announcing to customers:
- [ ] All tests passed with test cards
- [ ] Switched to LIVE Stripe API keys
- [ ] SSL/HTTPS working correctly
- [ ] Email delivery confirmed
- [ ] Webhooks configured and tested
- [ ] Database backups automated
- [ ] Error monitoring set up
- [ ] Support email/phone working
- [ ] Terms & conditions updated
- [ ] Privacy policy includes Stripe
- [ ] Staff trained on refund process
- [ ] Test real payment with small amount ($1)

---

## 🎉 CONGRATULATIONS!

Your secure payment system is ready for production!

**Remember:**
- Monitor payments daily at first
- Respond to customer inquiries promptly
- Keep Stripe API keys secure
- Regular security updates
- Backup database regularly

**Need Help?**
Review the code documentation or contact the development team.

---

**Last Updated:** January 2026
**Version:** 2.0 - Production Ready
