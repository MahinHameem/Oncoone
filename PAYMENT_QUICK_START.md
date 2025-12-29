# Payment System Setup & Quick Start Guide

## ✅ Installation Complete

Your OncoOne Payment Gateway system has been successfully implemented!

---

## 🚀 Quick Start

### 1. **First Time Setup**

```bash
# Install dependencies (already done)
pip install whitenoise

# Create database tables (already done)
python manage.py migrate

# Create superuser if not already created
python manage.py createsuperuser
```

### 2. **Run Development Server**

```bash
python manage.py runserver
```

Then visit:
- 🏠 Home: `http://localhost:8000/`
- 💳 Payment Portal: `http://localhost:8000/payment/`
- 👨‍💼 Admin Panel: `http://localhost:8000/admin/`

---

## 📋 Initial Configuration

### Step 1: Add Course Prices (IMPORTANT)

Before students can make payments, you must add course prices:

1. Go to `http://localhost:8000/admin/`
2. Log in with superuser credentials
3. Click on **Core** → **Course Prices**
4. Click **Add Course Price**
5. Fill in:
   - **Course Name**: (must match exactly as in registrations, e.g., "Oncology Esthetics")
   - **Price CAD**: (e.g., 400.00)
   - **Description**: (optional)
6. Click **Save**

**Example Prices to Add:**
- Course Name: `Oncology Esthetics` | Price: `400.00`
- Course Name: `Resilience Course` | Price: `350.00`
- Course Name: `Advanced Techniques` | Price: `450.00`

### Step 2: Test the Payment System

1. Go to `http://localhost:8000/payment/`
2. Enter a student ID (e.g., `1` if you have a registration with ID 1)
3. Follow the payment flow:
   - Select course and amount
   - Review payment summary
   - Enter test card details (see below)
   - Complete payment

**Test Card Numbers:**
- **Visa**: `4111 1111 1111 1111`
- **Mastercard**: `5555 5555 5555 4444`

Any future date for expiry (e.g., 12/2025)
Any 3-4 digit CVN (e.g., 123)
Any cardholder name

---

## 🎨 Frontend Integration

### Add Payment Button to Navigation

The payment button has been added to your homepage!

- ✅ Desktop Navigation: Shows "Payments" button
- ✅ Mobile: Includes payment link in nav menu
- Location: Top right of navbar

### Customize Payment Portal Styling

Edit CSS in templates:
```
/templates/payments/payment_portal_home.html
/templates/payments/payment_select_amount.html
/templates/payments/payment_summary.html
/templates/payments/payment_card_form.html
/templates/payments/payment_success.html
/templates/payments/payment_cancelled.html
```

---

## 🔍 Admin Panel Guide

### View All Payments

**Path**: `/admin/core/payment/`

Features:
- 📊 Filter by status (Pending, Completed, Failed, Cancelled)
- 🔍 Search by student ID or invoice number
- 📅 Filter by date range
- 💳 Filter by payment method
- 👁️ View full payment details

### View Course Prices

**Path**: `/admin/core/courseprice/`

Features:
- ➕ Add new courses
- ✏️ Edit prices
- 🗑️ Delete courses
- 🔍 Search by course name

### View Invoices

**Path**: `/admin/core/paymentinvoice/`

Features:
- 📄 View generated invoices
- 📧 Link to payment records
- 🔗 See invoice HTML

---

## 📧 Email Configuration

### Setting Up Email Notifications

Edit `backend/settings.py`:

```python
# For Gmail (example)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@oncoone.com'

# Admin notifications
ADMIN_EMAIL = 'admin@oncoone.com'
```

### For Production (Hostinger)

```python
# Hostinger SMTP settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.hostinger.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@yourdomain.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'
```

---

## 🗄️ Database Models

### Registration → Payment Flow

```
Registration (existing)
    ↓
    └─→ CoursePrice (new)
            ↓
        Payment (new)
            ↓
        PaymentInvoice (new)
```

**Key Fields in Payment:**
- `student_id`: Student's ID
- `course_name`: Course being paid for
- `payment_amount_cad`: Amount student pays (can be partial)
- `total_price_cad`: Full course fee
- `remaining_balance`: Amount still owed
- `tax_amount`: 5% GST
- `final_amount_cad`: Total (payment + tax)
- `status`: Payment status
- `invoice_number`: Unique invoice ID

---

## 🔐 Security Notes

✅ **What's Protected:**
- Card information (only last 4 digits stored)
- CVN never stored
- CSRF protection on all forms
- Student verification required

⚠️ **For Production:**
1. Use HTTPS only
2. Integrate with real payment processor (Stripe, PayPal, Square)
3. Enable Django security settings:
   ```python
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```
4. Store sensitive data in environment variables
5. Use Django admin permission groups

---

## 📊 Payment Status Codes

| Status | Meaning | Action |
|--------|---------|--------|
| `pending` | Payment initiated | Awaiting processing |
| `processing` | Payment being processed | In progress |
| `completed` | Payment successful | Invoice sent, record saved |
| `failed` | Payment declined/error | Show retry option |
| `cancelled` | User cancelled | No charges made |

---

## 🎯 Student Workflow

```
1. Student clicks "Payments" on homepage
   ↓
2. Enters Student ID (e.g., 123)
   ↓
3. System shows registered courses
   ↓
4. Student enters payment amount (partial or full)
   ↓
5. System calculates tax (5%)
   ↓
6. Student reviews payment details
   ↓
7. Student agrees to terms
   ↓
8. Student enters card details
   ↓
9. System processes payment
   ↓
10. Student sees confirmation + invoice
   ↓
11. Email sent with invoice
   ↓
12. Admin sees payment in dashboard
```

---

## 🐛 Troubleshooting

### Issue: "No module named 'whitenoise'"
**Solution**: 
```bash
pip install whitenoise
```

### Issue: "Student not found"
**Solution**:
- Verify student registration exists
- Try entering email address instead of ID
- Check database has registrations

### Issue: "Course price not found"
**Solution**:
- Add course price via admin panel
- Match course name EXACTLY as registered
- Go to `/admin/core/courseprice/` and add it

### Issue: "Payment not showing in admin"
**Solution**:
- Check database migrations: `python manage.py migrate`
- Verify payment completed successfully
- Check browser console for JavaScript errors

### Issue: "Email not sending"
**Solution**:
- Check email configuration in settings.py
- Verify ADMIN_EMAIL is set
- Check email credentials
- Review console for errors

---

## 📱 Mobile Responsiveness

Payment portal is fully responsive:
- ✅ Desktop (1920px+)
- ✅ Tablet (768px - 1024px)
- ✅ Mobile (320px - 767px)

All forms adapt to screen size with:
- Touch-friendly buttons
- Readable font sizes
- Proper spacing
- Full-width inputs

---

## 🎨 Customization

### Change Colors

Edit gradient colors in template files:
```html
<!-- Change from -->
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

<!-- To your colors -->
background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
```

### Change Text

All text can be edited in template HTML files in `/templates/payments/`

### Change Tax Rate

Edit in `core/views.py` - `payment_calculate_tax` function:
```python
tax_rate = Decimal('0.05')  # Change 0.05 to your rate (e.g., 0.10 for 10%)
```

---

## 📈 Next Steps

### Phase 2 Features:
1. ✅ Basic payment system (DONE)
2. 🔜 Real payment gateway (Stripe/PayPal)
3. 🔜 Installment/payment plans
4. 🔜 Refund processing
5. 🔜 Receipt downloads
6. 🔜 Payment analytics dashboard

### Integration Points:
- Stripe Connect for payment processing
- SendGrid or Mailgun for email
- AWS S3 for invoice storage
- Analytics platform for reporting

---

## 📚 Documentation Files

- 📄 **PAYMENT_SYSTEM.md** - Complete system documentation
- 📄 **This file** - Quick start guide
- 📁 **templates/payments/** - All template files

---

## ✨ Summary

Your OncoOne Payment Gateway is ready to use! Here's what's been set up:

✅ Complete payment portal system
✅ Student verification
✅ Course and amount selection  
✅ Payment summary review
✅ Card entry form
✅ Payment processing
✅ Invoice generation
✅ Email notifications
✅ Admin dashboard
✅ Database models
✅ API endpoints
✅ Security features
✅ Mobile responsive design

---

**Need Help?**
- Check `/templates/payments/` for template code
- Review `core/views.py` for payment logic
- Check `core/models.py` for database structure
- See `core/urls.py` for URL routing

Happy coding! 🚀
