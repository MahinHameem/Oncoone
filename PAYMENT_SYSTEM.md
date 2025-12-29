# OncoOne Payment Gateway System

## Overview

The OncoOne Payment Gateway is a complete online payment portal system that allows students to make course fee payments using credit/debit cards (Visa/Mastercard).

---

## System Features

### 1. **Payment Portal Home** (`/payment/`)
- Students enter their **Student ID** or **Registration ID** to access the payment system
- The system verifies the student exists in the database
- Displays all registered courses for the student

### 2. **Course Selection & Amount Entry** (`/payment/select-course/<student_id>/`)
- Student can view:
  - Course name
  - Full course fee (in CAD)
- Student enters the **payment amount** they want to pay (partial or full)
- System validates the amount is within the course fee range
- Real-time calculation of **tax (5% GST)** and **total amount**

### 3. **Payment Summary** (`/payment/summary/<student_id>/`)
- Review all payment details:
  - Student ID and name
  - Course information
  - Payment amount (CAD)
  - Tax amount (5% GST)
  - Total amount to pay
  - **Remaining balance** (balance after this payment)
- Student must **agree to terms and conditions** before proceeding

### 4. **Card Entry & Payment** (`/payment/card-entry/<student_id>/`)
- Secure card information entry form
- Fields:
  - Card type (Visa/Mastercard)
  - Card number (13-19 digits)
  - Cardholder name
  - Expiry month and year
  - CVN/CVC (3-4 digits)
- Security notice displayed to reassure students

### 5. **Payment Processing** (`/api/payment/process/`)
- Card details are validated
- Payment is processed (demo/simulated)
- Payment record is created in database
- Invoice is generated
- Confirmation email is sent to student

### 6. **Payment Success** (`/payment/success/<payment_id>/`)
- Confirmation page showing:
  - ✓ Payment successful
  - Invoice number and transaction ID
  - Full payment details
  - Remaining balance (if any)
  - Card last 4 digits (masked for security)
- Options to:
  - Download invoice
  - Make another payment
  - Return to home

### 7. **Payment Cancelled** (`/payment/cancelled/<student_id>/`)
- If user cancels payment during card entry
- Shows that no charges were made
- Option to return to payment portal or home

---

## Database Models

### 1. **CoursePrice**
```python
- course_name: CharField (unique)
- price_cad: DecimalField (10,2)
- description: TextField
- created_at: DateTimeField (auto)
- updated_at: DateTimeField (auto)
```

### 2. **Payment**
```python
- registration: ForeignKey (Registration)
- student_id: CharField
- course_name: CharField
- total_price_cad: DecimalField (full course fee)
- payment_amount_cad: DecimalField (amount student pays)
- tax_amount: DecimalField (5% of payment amount)
- final_amount_cad: DecimalField (payment + tax)
- status: CharField (pending, processing, completed, failed, cancelled)
- payment_method: CharField (visa, mastercard)
- card_holder_name: CharField
- card_last_four: CharField (for security)
- transaction_id: CharField (unique transaction ID)
- invoice_number: CharField (unique invoice number)
- created_at: DateTimeField
- updated_at: DateTimeField
- completed_at: DateTimeField
```

### 3. **PaymentInvoice**
```python
- payment: OneToOneField (Payment)
- invoice_pdf: FileField
- invoice_html: TextField (HTML invoice)
- generated_at: DateTimeField
```

---

## URL Routes

### Frontend Routes
| Route | Purpose |
|-------|---------|
| `/payment/` | Payment portal home (student ID verification) |
| `/payment/select-course/<student_id>/` | Select course and amount |
| `/payment/summary/<student_id>/` | Review payment summary |
| `/payment/card-entry/<student_id>/` | Enter card details |
| `/payment/success/<payment_id>/` | Payment success confirmation |
| `/payment/cancelled/<student_id>/` | Payment cancelled page |

### API Routes
| Route | Method | Purpose |
|-------|--------|---------|
| `/api/payment/verify-student/` | POST | Verify student and get courses |
| `/api/payment/calculate-tax/` | POST | Calculate tax on amount |
| `/api/payment/process/` | POST | Process card payment |

---

## Admin Panel Features

### Django Admin (`/admin/`)

1. **Course Price Management**
   - Add/Edit/Delete course prices
   - Set price in CAD for each course
   - View creation and update timestamps

2. **Payment Management**
   - View all payments with status
   - Filter by status, date, or payment method
   - Search by student ID or invoice number
   - View detailed payment information

3. **Invoice Management**
   - View generated invoices
   - Link to associated payments

---

## How to Use - Admin Setup

### 1. Add Course Prices
```
Go to Django Admin → Core → Course Prices → Add Course Price
- Course Name: (e.g., "Oncology Esthetics Course")
- Price CAD: (e.g., 400.00)
- Description: (optional)
```

### 2. View Payments
```
Go to Django Admin → Core → Payments
- Filter by status to see pending/completed/failed payments
- Click on a payment to view full details
- Check remaining balance
```

---

## Flow Diagram

```
Student Clicks "Payments" Button
    ↓
Enter Student ID/Registration ID
    ↓
System Verifies Student & Shows Courses
    ↓
Select Course & Enter Payment Amount
    ↓
Review Payment Summary
    ↓
Agree to Terms & Conditions
    ↓
Enter Card Details (Visa/Mastercard)
    ↓
Process Payment
    ↓
    ├─→ SUCCESS: Show confirmation, send invoice email, offer to pay more
    ├─→ FAILED: Show error, allow retry
    └─→ CANCELLED: Return to home or payment portal
```

---

## Payment Details

### Tax Calculation
- **Tax Rate**: 5% (GST - Canadian)
- **Calculation**: `tax = payment_amount × 0.05`
- **Total to Pay**: `payment_amount + tax`

### Invoice Details Included
- Invoice number (INV-YYYYMMDDHHMMSS-##### format)
- Student ID and name
- Course name
- Payment amount
- Tax amount
- Total paid
- Remaining balance
- Card type and last 4 digits
- Transaction ID
- Date/Time

---

## Security Features

1. **Card Information**
   - Only last 4 digits stored in database
   - Full card numbers not stored
   - CVN not stored (not required by PCI compliance for demo)

2. **Payment Status**
   - Only authorized staff can view payment details in admin
   - Payment records linked to registered students

3. **CSRF Protection**
   - All forms include CSRF token
   - API calls validate CSRF

4. **Email Notifications**
   - Students receive payment confirmation emails
   - Invoices sent to registered email address

---

## Templates

All templates are located in `/templates/payments/`:

1. **payment_portal_home.html** - Student ID entry
2. **payment_select_amount.html** - Course and amount selection
3. **payment_summary.html** - Payment review
4. **payment_card_form.html** - Card entry form
5. **payment_success.html** - Success confirmation
6. **payment_cancelled.html** - Cancellation page

All templates are styled with:
- Bootstrap CSS
- Custom gradient design (purple/blue theme)
- Responsive mobile-friendly layout
- Loading spinners and animations

---

## API Responses

### Verify Student
**Request**: POST `/api/payment/verify-student/`
```json
{
  "student_id": "123"
}
```
**Response**: 
```json
{
  "status": "ok",
  "student": {
    "id": 123,
    "name": "John Doe",
    "email": "john@example.com",
    "contact": "555-1234"
  },
  "courses": [
    {
      "id": 1,
      "name": "Oncology Esthetics",
      "price": "400.00",
      "description": "..."
    }
  ],
  "course_count": 1
}
```

### Process Payment
**Request**: POST `/api/payment/process/`
```json
{
  "student_id": "123",
  "payment_amount": "200.00",
  "tax_amount": "10.00",
  "total_amount": "210.00",
  "card_type": "visa",
  "card_number": "4111111111111111",
  "card_holder": "John Doe",
  "expiry_month": "12",
  "expiry_year": "2025",
  "cvn": "123",
  "terms_agreed": true
}
```
**Response**:
```json
{
  "status": "success",
  "payment_id": 1,
  "invoice_number": "INV-20251229120000-00001",
  "transaction_id": "uuid-here"
}
```

---

## Environment Setup

### Required Packages
```
Django >= 6.0
whitenoise (for static file serving)
```

### Database
```
SQLite3 (default) or PostgreSQL
```

### Settings Required
```python
# backend/settings.py
- ADMIN_EMAIL configured
- DEFAULT_FROM_EMAIL configured
- Static files configuration
```

---

## Troubleshooting

### 1. Student Not Found
- Verify student ID is correct
- Check registration exists in database
- Try using email address instead of ID

### 2. Payment Processing Issues
- Verify card number format (13-19 digits)
- Check expiry date is in future
- Ensure CVN is 3-4 digits

### 3. Email Not Sending
- Check ADMIN_EMAIL and DEFAULT_FROM_EMAIL in settings
- Verify email backend is configured
- Check email service credentials

### 4. Missing Course Prices
- Add course prices via Django Admin
- Match course names exactly as registered
- Price must be in CAD dollars

---

## Future Enhancements

1. **Real Payment Gateway Integration**
   - Stripe integration
   - PayPal integration
   - Square integration

2. **Features**
   - Payment plans/installments
   - Refund processing
   - Receipt downloads
   - Payment history per student
   - Multiple course payments
   - Discount codes

3. **Reporting**
   - Payment analytics dashboard
   - Revenue reports
   - Student payment status reports

---

## Support

For issues or questions:
1. Check Django Admin for payment records
2. Review email logs for notifications
3. Verify student registration exists
4. Check CoursePrice entries in admin panel

---

**Last Updated**: December 29, 2025
**Version**: 1.0
