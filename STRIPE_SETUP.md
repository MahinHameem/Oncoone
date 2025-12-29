# Stripe Setup Guide for OncoOne

## Overview
This guide explains how to set up Stripe payment processing for OncoOne. All payments will go directly to your OncoOne business account in Canada.

## Step 1: Create Stripe Account

1. **Go to Stripe:** https://dashboard.stripe.com/register
2. **Select Country:** Canada
3. **Fill in Business Information:**
   - Business Name: OncoOne
   - Email: info@oncoesthetics.ca
   - Website: oncoesthetics.ca

## Step 2: Get Your API Keys

1. **Login to Stripe Dashboard:** https://dashboard.stripe.com
2. **Go to: Developers → API Keys**
3. **You'll see:**
   - **Publishable Key** (starts with `pk_test_` or `pk_live_`)
   - **Secret Key** (starts with `sk_test_` or `sk_live_`)

### Test Mode (Recommended for Testing)
- Use keys starting with `pk_test_` and `sk_test_`
- Test card numbers:
  - Visa: `4242 4242 4242 4242`
  - Mastercard: `5555 5555 5555 4444`
  - Any future expiry, any 3-digit CVN

### Live Mode (Production)
- Use keys starting with `pk_live_` and `sk_live_`
- Real payments will be processed
- Funds transfer to your bank account

## Step 3: Update .env File

Edit `.env` in your project root:

```
# STRIPE PAYMENT CONFIGURATION (Canada)
STRIPE_PUBLIC_KEY=pk_test_YOUR_PUBLIC_KEY_HERE
STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_test_YOUR_WEBHOOK_SECRET_HERE

# Business Settings
BUSINESS_NAME=OncoOne
BUSINESS_EMAIL=info@oncoesthetics.ca
BUSINESS_CURRENCY=cad
STRIPE_STATEMENT_DESCRIPTOR=OncoOne Payments
```

Replace the key values with your actual keys from Stripe dashboard.

## Step 4: Set Up Webhook (Optional but Recommended)

Webhooks notify your app when Stripe events occur (successful payment, failed charge, etc.).

### To Set Up Webhooks:

1. **Go to: Developers → Webhooks**
2. **Add endpoint:**
   - URL: `https://yourdomain.com/api/payment/webhook/`
   - Events to listen for:
     - `payment_intent.succeeded`
     - `payment_intent.payment_failed`
     - `charge.refunded`

3. **Get Webhook Secret:**
   - Click the endpoint you created
   - Copy "Signing Secret"
   - Add to .env as `STRIPE_WEBHOOK_SECRET`

## Step 5: Connect Bank Account

1. **In Stripe Dashboard:**
   - Go to: Settings → Bank accounts and transfers
   - Add your Canadian bank account
   - Verify transfers (Stripe will send 2 small deposits)

2. **Payout Settings:**
   - Go to: Settings → Payouts
   - Set schedule (daily, weekly, monthly)
   - All payments go to this account

## Payment Flow with Stripe

```
1. Student enters registration ID/email
2. Select course and amount to pay
3. Review payment summary
4. Enter card details (Stripe form)
5. Card info sent to Stripe (NEVER touches your server)
6. OTP sent to student email
7. Student enters OTP to confirm
8. Stripe processes payment (2.2% + $0.30 CAD)
9. Funds go to your OncoOne bank account
10. Invoice generated and emailed
```

## Pricing (Canada)

| Item | Cost |
|------|------|
| **Per Transaction** | 2.2% + $0.30 CAD |
| **Example:** $400 course | 2.2% = $8.80 + $0.30 = **$9.10 fee** |
| **Example:** $800 course | 2.2% = $17.60 + $0.30 = **$17.90 fee** |

### Pricing Calculation:
- **Amount Charged:** CAD $100.00
- **Stripe Fee:** (100 × 0.022) + 0.30 = $2.50
- **You Receive:** $97.50

## Test Transactions

### Testing Payment Success:
1. Card: `4242 4242 4242 4242`
2. Expiry: Any future date
3. CVN: Any 3 digits
4. Name: Any name

Result: Payment succeeds ✅

### Testing Payment Failure:
1. Card: `4000 0000 0000 0002`
2. Expiry: Any future date
3. CVN: Any 3 digits

Result: Payment fails ✗ (for testing error handling)

## Admin Panel

### View Payments in Django Admin:
1. Go to: http://localhost:8000/admin
2. Payments section shows:
   - Student name
   - Course name
   - Amount paid
   - Stripe transaction ID
   - Payment status (pending, completed, failed)
   - Invoice number

### View Transactions on Stripe:
1. https://dashboard.stripe.com/payments
2. See all transactions
3. Check payment details
4. Issue refunds if needed

## Security Notes

✅ **What We Do:**
- Card details are entered directly into Stripe form
- Your server NEVER sees card numbers
- PCI compliance automatically handled by Stripe
- OTP verification adds extra security layer
- All transactions logged with transaction IDs

❌ **What We Don't Do:**
- Store full card numbers
- Store CVN codes
- Handle raw card data
- Process payments locally

## Troubleshooting

### Error: "Invalid API Key"
- Check `.env` has correct STRIPE_SECRET_KEY
- Make sure you're using secret key, not public key
- Verify key is from correct mode (test vs live)

### Error: "Webhook signature verification failed"
- Check STRIPE_WEBHOOK_SECRET matches dashboard
- Webhook secret is different from API keys
- Get it from: Developers → Webhooks → Click endpoint

### Payment appears in Stripe but not in app
- Check webhook is properly configured
- Webhook may be processing in background (takes <5 seconds)
- Check app logs for errors

### Funds not appearing in bank account
- First transfer takes 2-5 business days
- Check bank account is verified in Stripe settings
- Minimum payout amount: $2.50 CAD
- Check payout schedule settings

## Contact & Support

- **Stripe Support:** https://support.stripe.com
- **Stripe Documentation:** https://stripe.com/docs
- **Dashboard:** https://dashboard.stripe.com

## Next Steps

1. ✅ Create Stripe account
2. ✅ Get API keys (test first)
3. ✅ Update .env with keys
4. ✅ Restart Django server
5. ✅ Test payment flow with test card
6. ✅ Verify payment appears in Stripe dashboard
7. ✅ Switch to live keys when ready
8. ✅ Connect real bank account
