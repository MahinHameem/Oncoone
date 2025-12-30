# Quick Reference - Multiple Course Registration

## What Changed?

### Before ❌
- One registration = One course only
- Same email couldn't register twice
- Course field stored on Registration model
- No prerequisite tracking per course

### After ✅
- One registration = Multiple courses
- Same student can register for different courses
- New StudentCourseEnrollment tracks each course separately
- Prerequisite proof stored per course enrollment
- Each course can have separate payment

---

## Database Structure

```
Registration (Student)
├── email (unique)
├── name
├── contact
└── course_enrollments → StudentCourseEnrollment (Many)
                           ├── course_name
                           ├── has_prerequisite
                           ├── proof (file)
                           ├── enrollment_status
                           └── payments → Payment (Many)
                                          ├── course_name
                                          ├── amount
                                          └── status
```

---

## Form Flow (Frontend)

```
┌─────────────────────────────────────────┐
│   Step 1: Select Course                │
│   ○ Oncology Esthetics Certificate      │
│   ○ Pre-Certificate Bridge Course       │
└─────────────────────────────────────────┘
              ↓
   ┌─────────────────────────────────┐
   │ Selected Oncology? YES           │
   └─────────────────────────────────┘
         ↓                      ↓
   ┌──────────────┐      ┌───────────────┐
   │ Step 2a:    │      │ Step 2b:      │
   │ "Have cert?"│      │ No questions! │
   │ YES → File  │      └───────────────┘
   │ NO → Info   │
   └──────────────┘
              ↓
   ┌─────────────────────────────────┐
   │   Step 3: Contact Info          │
   │   • Name                        │
   │   • Email                       │
   │   • Contact                     │
   └─────────────────────────────────┘
              ↓
   ┌─────────────────────────────────┐
   │ Submit & Go to Payment Portal   │
   └─────────────────────────────────┘
```

---

## API Request Example

**Endpoint:** POST `/api/register/`

### Case 1: Oncology with Certificate
```javascript
{
  name: "Jane Doe",
  email: "jane@example.com",
  contact: "555-0123",
  course: "Oncology Esthetics Certificate",
  hasQualification: "yes",
  proof: [File object - PDF/JPG/PNG, max 5MB]
}
```

### Case 2: Oncology without Certificate
```javascript
{
  name: "John Smith",
  email: "john@example.com",
  contact: "555-0456",
  course: "Oncology Esthetics Certificate",
  hasQualification: "no"
  // No proof file needed
}
```

### Case 3: Bridge Course
```javascript
{
  name: "Sarah Jones",
  email: "sarah@example.com",
  contact: "555-0789",
  course: "Pre-Certificate Bridge Course",
  hasQualification: "no"  // Will be ignored
  // No prerequisite questions for bridge
}
```

---

## API Response Example

```json
{
  "status": "ok",
  "id": 5,
  "registration_id": "REG-20250129-000005",
  "enrollment_id": 12,
  "message": "Registration for Oncology Esthetics Certificate successful! Your Registration ID is: REG-20250129-000005"
}
```

---

## Common Queries

### Get all courses for a student
```python
student = Registration.objects.get(email="jane@example.com")
courses = student.course_enrollments.all()

for enrollment in courses:
    print(f"{enrollment.course_name} - {enrollment.enrollment_status}")
```

### Check if student can pay for a course
```python
enrollment = StudentCourseEnrollment.objects.get(id=1)
if enrollment.has_paid():
    print("Already paid!")
else:
    print("Ready to pay")
```

### Get all pending payments for a student
```python
student = Registration.objects.get(id=5)
pending = student.payments.filter(status='pending')

for payment in pending:
    print(f"{payment.course_name}: ${payment.final_amount_cad}")
```

### Admin: Find all students waiting for prerequisites
```python
pending_enrollments = StudentCourseEnrollment.objects.filter(
    enrollment_status='pending',
    has_prerequisite=True
)
```

---

## Admin Tasks

### View Student Info
1. Go to Admin → Registrations
2. Click student name
3. See all courses in related StudentCourseEnrollments

### Approve Prerequisites
1. Go to Admin → StudentCourseEnrollment
2. Filter by "pending" status
3. Click enrollment
4. Change status to "approved"
5. Save

### Track Payments
1. Go to Admin → Payments
2. Filter by enrollment (shows which course)
3. See payment status
4. Filter by status (pending/completed)

---

## Important Fields

### StudentCourseEnrollment
| Field | Type | Purpose |
|-------|------|---------|
| registration | FK | Which student |
| course_name | CharField | Course title |
| has_prerequisite | Boolean | Has cert (True) or needs bridge (False) |
| proof | FileField | Prerequisite proof file |
| enrollment_status | Choice | pending→approved→in_progress→completed |
| enrolled_at | DateTime | When they enrolled |

### Payment
| Field | Type | Purpose |
|-------|------|---------|
| registration | FK | Which student |
| **enrollment** | FK | Which course enrollment (NEW) |
| course_name | CharField | Course for this payment |
| status | Choice | Payment status |
| invoice_number | CharField | Receipt number |

---

## Errors & Solutions

### Error: "You are already registered for [Course]"
- **Cause:** Student tried to register for same course twice with same email
- **Solution:** Student should register for a different course

### Error: "Proof of prerequisite is required"
- **Cause:** Selected Oncology + "Yes, I have cert" but no file uploaded
- **Solution:** Upload PDF/JPG/PNG file (max 5MB)

### Error: "Unsupported file type"
- **Cause:** Uploaded file is not PDF, JPG, or PNG
- **Solution:** Convert file to accepted format

### Error: "File too large"
- **Cause:** File exceeds 5MB limit
- **Solution:** Compress file before uploading

---

## Testing Checklist

- [ ] Register Bridge Course - works ✓
- [ ] Register Oncology + Yes + upload - works ✓
- [ ] Register Oncology + No + no upload - works ✓
- [ ] Same email, different course - allowed ✓
- [ ] Same email, same course - blocked ✓
- [ ] File size validation (< 5MB) ✓
- [ ] File type validation (PDF/JPG/PNG) ✓
- [ ] Emails sent to admin & student ✓
- [ ] Admin sees all enrollments ✓
- [ ] Payment links to correct enrollment ✓

---

## Next Steps

1. **Test the forms** - Register for different courses
2. **Update payment portal** - Show course selector
3. **Update payment views** - Link enrollment to payment
4. **Test payments** - Pay for different courses
5. **Admin workflow** - Review & approve registrations
6. **Production** - Deploy & monitor

---

## Files Modified

✅ core/models.py - Registration & StudentCourseEnrollment models
✅ core/views.py - register_view (updated for multiple courses)
✅ core/admin.py - Updated admin interfaces
✅ templates/products.html - Updated form with course selector
✅ core/migrations/0007_* - Database schema changes

## Documentation Created

📄 MULTIPLE_COURSES.md - Full technical documentation
📄 PAYMENT_INTEGRATION.md - Payment portal integration guide
📄 QUICK_REFERENCE.md - This file
