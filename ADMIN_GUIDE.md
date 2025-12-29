# Admin Dashboard - Payment System Management

## 🎯 Overview

The Django admin panel now includes complete payment management capabilities. Admins can:
- Monitor all payments and transactions
- Manage course prices
- View payment invoices
- Track student payment history
- Filter and search payments

---

## 📊 Admin Features

### 1. Course Price Management

**Location**: `/admin/core/courseprice/`

#### Features:
- ➕ Add new course prices
- ✏️ Edit existing prices
- 🗑️ Delete courses
- 🔍 Search by course name
- 📅 View creation/update timestamps

#### Steps to Add a Course:

1. Go to Django Admin: `http://localhost:8000/admin/`
2. Click **Core** in the sidebar
3. Click **Course Prices**
4. Click **Add Course Price** button
5. Fill in:
   ```
   Course Name: Oncology Esthetics
   Price CAD: 400.00
   Description: (optional) Professional certification course
   ```
6. Click **Save**

#### Important Notes:
- Course name must match EXACTLY as registered in the Registration model
- Price must be in Canadian dollars (CAD)
- You can update prices anytime (students see current price)

---

### 2. Payment Management (Main)

**Location**: `/admin/core/payment/`

#### List View Features:

**Columns Displayed:**
- 📄 Invoice Number (e.g., INV-20251229120000-00001)
- 👤 Student ID
- 📚 Course Name
- 💰 Payment Amount (CAD)
- ✅ Status (Pending/Completed/Failed/Cancelled)
- 📅 Completion Date

#### Filters Available:
- 🔴 **By Status**: Filter to see only completed, failed, or pending payments
- 📅 **By Date**: Filter by creation or completion date
- 💳 **By Payment Method**: Filter by Visa or Mastercard
- 🔍 **Search**: Search by Student ID, Invoice Number, or Course Name

#### Example Queries:
- "Show all completed payments from today" → Status: Completed + Date Filter
- "Show all Visa payments" → Payment Method: Visa
- "Find payment for student 123" → Search: "123"

### Detailed Payment View

Click any payment to see full details:

**Student Information Section:**
- Registration (linked to student record)
- Student ID
- Student name (from registration)
- Email
- Contact

**Course & Payment Details:**
- Course name
- Full course fee (total_price_cad)
- Payment amount (what student paid)
- Tax amount (5% GST)
- Final amount (total charged)

**Payment Method:**
- Type (Visa/Mastercard)
- Last 4 digits of card (e.g., 1111)
- Cardholder name

**Transaction Details:**
- Status
- Transaction ID (unique identifier)
- Invoice number (unique invoice reference)

**Timestamps:**
- Created at (when payment was initiated)
- Updated at (last modification)
- Completed at (when payment was processed)

---

### 3. Invoice Management

**Location**: `/admin/core/paymentinvoice/`

#### Features:
- 📄 View all generated invoices
- 🔗 Link to payment records
- 📊 View invoice HTML content
- 📅 Check generation dates

#### What's in an Invoice:
- Invoice number
- Student details
- Course information
- Payment breakdown:
  - Payment amount
  - Tax (5% GST)
  - Total paid
  - Remaining balance
- Card information (last 4 digits only)
- Transaction ID
- Date and time

---

## 💡 Use Cases

### Use Case 1: A student made a payment and wants confirmation

```
1. Go to /admin/core/payment/
2. Search for student ID (e.g., "123")
3. Click on the payment record
4. Verify:
   - Status: "Completed"
   - Amount and tax
   - Invoice number
5. Share invoice number with student
```

### Use Case 2: Track daily revenue

```
1. Go to /admin/core/payment/
2. Filter by Status: "Completed"
3. Filter by Date: Today
4. View all completed payments
5. Calculate total from the list
```

### Use Case 3: Update course pricing

```
1. Go to /admin/core/courseprice/
2. Click on course to edit
3. Change price to new amount
4. Save
5. Future payments will use new price
```

### Use Case 4: Monitor payment method popularity

```
1. Go to /admin/core/payment/
2. Filter by Payment Method: "Visa"
3. Count results
4. Repeat for Mastercard
5. Compare usage
```

### Use Case 5: Find failed payments

```
1. Go to /admin/core/payment/
2. Filter by Status: "Failed"
3. Contact students to retry
4. Offer assistance
```

---

## 🔐 Permissions & Security

### Admin Access Control

Only superusers and staff members with specific permissions can:
- View payments
- Edit course prices
- Delete records
- Access the admin panel

### What's Protected:
- ✅ Card details (only last 4 digits visible)
- ✅ CVN/CVC (never stored)
- ✅ Full payment records (admin-only access)
- ✅ Student email addresses

### To Grant Permissions:

1. Go to `/admin/auth/user/`
2. Click on a user
3. Check: **Is Staff** and **Is Superuser** (for full admin access)
4. Or assign specific permissions in the Permissions section
5. Save

---

## 📈 Payment Status Workflow

```
Student initiates payment
    ↓
status = "pending"
    ↓
Payment processed
    ↓
    ├─→ Success → status = "completed" → Invoice sent
    ├─→ Failed → status = "failed" → Show error to student
    └─→ Cancelled → status = "cancelled" → No charges made
```

### Status Breakdown:

| Status | What It Means | Admin Action |
|--------|---------------|--------------|
| **pending** | Payment initiated, not completed | Wait or contact student |
| **processing** | Payment is being processed | Monitor in progress |
| **completed** | ✅ Payment successful | Invoice sent, funds received |
| **failed** | ❌ Card declined or error | Contact student, offer retry |
| **cancelled** | 🚫 Student cancelled | No charges made, no action needed |

---

## 📊 Reports & Analytics

### Manual Reporting (from admin panel)

**Total Revenue This Month:**
1. Filter: Status = "Completed"
2. Filter: Date Range = This Month
3. Add up all "final_amount_cad" values

**Payment Success Rate:**
1. Count Completed payments
2. Divide by Total payments
3. Multiply by 100 = Success %

**Popular Payment Methods:**
1. Filter: Status = "Completed"
2. Filter: Payment Method = "Visa"
3. Count results
4. Repeat for Mastercard

**Courses by Revenue:**
1. For each course in CoursePrice
2. Filter payments: Status = "Completed", Course = Course Name
3. Sum payment amounts

---

## 🛠️ Admin Customization

### Add Custom Columns

Edit `core/admin.py` - PaymentAdmin class:

```python
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # Add to list_display to show more columns
    list_display = ('invoice_number', 'student_id', 'course_name', 
                   'payment_amount_cad', 'tax_amount', 'final_amount_cad', 
                   'status', 'payment_method', 'completed_at')
```

### Change Filter Options

```python
# Edit list_filter to change available filters
list_filter = ('status', 'payment_method', 'created_at', 'completed_at')
```

### Add Search Fields

```python
# Edit search_fields to search by more fields
search_fields = ('student_id', 'invoice_number', 'course_name', 
                'registration__name', 'registration__email')
```

---

## 🎨 Admin Interface Tips

### Keyboard Shortcuts:
- **Ctrl/Cmd + S**: Save
- **Tab**: Move to next field
- **Shift + Tab**: Move to previous field

### Bulk Actions:
1. Select multiple payments with checkboxes
2. Choose action from dropdown
3. Click "Go"

### Filters on Right:
- Click filter criteria to refine list
- Multiple filters work together (AND logic)
- Dates can be specific or ranges

### Search:
- Type in search box to find records
- Searches multiple fields at once
- Enter to search (or button click)

---

## 📧 Email Integration

### Invoice Email Content:

When a payment is completed, student receives:

```
Subject: Payment Confirmation - Invoice [Invoice Number]

Hi [Student Name],

Your payment has been successfully processed!

Invoice Number: INV-20251229120000-00001
Student ID: 123
Course: Oncology Esthetics
Payment Amount: CAD $200.00
Tax (5% GST): CAD $10.00
Total Paid: CAD $210.00
Remaining Balance: CAD $190.00

Card Used (Last 4): 1111
Transaction ID: abc123def456

Please keep this email for your records. You can download your 
invoice from your payment portal.

– OncoOne Team
```

### To Resend Invoice:

Currently must be done manually. Future enhancement will add button to admin.

---

## 🔍 Troubleshooting Admin Issues

### Issue: Payment not showing in list
**Solution:**
- Verify payment status is "completed"
- Check date filters
- Search by student ID

### Issue: Can't see student name in payment
**Solution:**
- Edit PaymentAdmin in admin.py
- Add `registration__name` to fields

### Issue: Course price won't update
**Solution:**
- Click "Save" button
- Hard refresh browser (Ctrl+F5)
- Verify in list view updates

### Issue: Filter options missing
**Solution:**
- Check list_filter in PaymentAdmin
- Add missing filters if needed
- Restart Django server

---

## 💼 For Production Deployment

### Admin Security:

1. **Create Admin User:**
```bash
python manage.py createsuperuser
# Username: admin
# Password: (strong password)
# Email: admin@oncoone.com
```

2. **Change Admin URL** (hide from bots):
Edit `backend/urls.py`:
```python
# Change from /admin/ to something unique
path('secure-admin-panel/', admin.site.urls),
```

3. **Enable Security Headers:**
Edit `backend/settings.py`:
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

4. **Enable Admin Logging:**
```python
# Set up audit trail of admin actions
```

---

## 📞 Support

**Need to check something?**
1. Go to `/admin/`
2. Choose what you need:
   - Course Prices → Manage pricing
   - Payments → Monitor transactions
   - Invoices → View receipts

**Common questions:**
- "Where's my payment?" → Search student ID in Payments
- "What's the course fee?" → Check Course Prices
- "Did they agree to terms?" → Check Payment record
- "When was payment made?" → See "completed_at" date

---

**Last Updated**: December 29, 2025
**Admin Version**: 1.0
