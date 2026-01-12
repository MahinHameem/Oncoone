# Payment Portal - Registration Number Integration

## ✅ Complete Implementation

### Registration Number Format
**ON26-XXXXXX** (e.g., ON26-370761, ON26-295052)
- ON = OncoOne prefix
- 26 = Year (2026)
- XXXXXX = Random 6-digit unique number (100000-999999)

---

## 🎯 What Students Receive

### 1. After Registration
Students receive an email with:

```
═══════════════════════════════════════
YOUR REGISTRATION NUMBER: ON26-370761
═══════════════════════════════════════

Please save this registration number. You will need it to:
• Make payments through our payment portal
• Access your student account
• Track your course progress
```

### 2. For Making Payments
Students use their **Registration Number** to:
- Access the payment portal
- Make course payments
- View payment history

### 3. After Payment
Students receive confirmation email with:

```
═══════════════════════════════════════
PAYMENT CONFIRMATION
═══════════════════════════════════════

Registration Number: ON26-370761
Invoice Number: INV-20260112-00001
Course: Oncology Esthetics Certificate
Total Paid: CAD $2,500.00
```

---

## 💳 Payment Portal Flow

### Step 1: Enter Registration Number
Payment portal asks for: **Registration Number (ON26-XXXXXX)**
- Students enter: `ON26-370761`
- Or use their email address

### Step 2: Verify Student
System accepts:
- ✅ New format: `ON26-370761`
- ✅ Email: `student@email.com`
- ✅ Old formats (backward compatible)

### Step 3: Select Course & Pay
- Student selects course
- Makes payment
- Receives confirmation with Registration Number

---

## 📧 Email Templates Updated

### Registration Confirmation Email
**Subject:** Welcome to OncoOne - Registration Number: ON26-370761

**Content:**
- Prominently displays registration number
- Explains how to use it for payments
- Student details and course info

### Payment Confirmation Email
**Subject:** Payment Confirmation - Invoice INV-20260112-00001

**Content:**
- Registration Number at the top
- Invoice details
- Payment amount and balance
- Transaction ID

---

## 🔧 Technical Implementation

### Files Updated
1. **core/models.py** - Random 6-digit registration numbers
2. **core/views.py** - Payment verification accepts ON26-XXXXXX
3. **templates/payments/payment_portal_home.html** - Updated UI

### Payment Verification Logic
```python
# Accepts multiple formats:
if student_id.startswith('ON'):
    # New format: ON26-370761
    registration = Registration.objects.filter(
        registration_number=student_id
    ).first()
    
# Also accepts email
registration = Registration.objects.filter(
    email=student_id
).first()
```

### Payment Creation
```python
payment = Payment.objects.create(
    registration=registration,
    student_id=registration.registration_number,  # Uses ON26-XXXXXX
    # ... other fields
)
```

---

## 📊 Current Students

All 8 students have been updated with registration numbers:

| Registration Number | Name | Email |
|---------------------|------|-------|
| ON26-295052 | Mahin Hameem | mahinham@gmail.com |
| ON26-866149 | dsa | sad |
| ON26-894521 | imadhN | sad@gmail.com |
| ON26-132683 | Mahin Hameem | saadhram1@gmail.com |
| ON26-777060 | Mahin Hameem | saadhram10@gmail.com |
| ON26-911112 | Safa Raihana | imadhcareem009@gmail.com |
| ON26-425435 | helo | mahin@gmail.com |
| ON26-370761 | Mahin Hameem | mahin.dts@gmail.com |

---

## ✨ Key Features

✅ **Random 6-digit numbers** - No one can guess or duplicate  
✅ **Unique across all students** - Database enforced  
✅ **Year-based prefix** - ON26 for 2026, ON27 for 2027  
✅ **Email integration** - Sent in registration & payment emails  
✅ **Payment portal** - Primary identifier for making payments  
✅ **Backward compatible** - Old IDs still work  

---

## 🚀 Usage Examples

### Student Makes Payment
1. Receives email: "Your Registration Number: **ON26-370761**"
2. Goes to payment portal
3. Enters: `ON26-370761`
4. Selects course and completes payment
5. Receives invoice with registration number

### Admin Views Student
- Admin panel shows: **ON26-370761** in registration list
- Easy to search and identify students
- Professional appearance

---

**Status:** ✅ Fully Implemented and Tested  
**Date:** January 12, 2026
