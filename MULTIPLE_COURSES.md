# Multiple Course Registration Implementation

## Overview
Students can now register for **multiple courses** in the system. The registration system allows:
- Same student email to register for different courses
- Per-course prerequisite validation
- Per-course payment tracking
- Course-specific enrollment management

## Database Schema Changes

### Models Updated

#### 1. **Registration** (Simplified)
```python
- name: CharField
- email: EmailField (unique) 
- contact: CharField
- created_at, updated_at: DateTime
```
**Removed fields:** `course`, `auto_bridge`, `proof`, `proof_name`, `proof_mime`, `proof_data`

**New method:**
- `get_enrolled_courses()` - Returns all courses enrolled in

---

#### 2. **StudentCourseEnrollment** (NEW)
Tracks each course enrollment for a student:

```python
- registration: ForeignKey(Registration)
- course_name: CharField
- has_prerequisite: BooleanField (True = has cert, False = needs bridge)
- proof: FileField (for prerequisite proof)
- proof_name, proof_mime, proof_data: Storage fields
- enrollment_status: Choice (pending, approved, in_progress, completed)
- enrolled_at, updated_at: DateTime
```

**Unique Constraint:** `unique_together(['registration', 'course_name'])`
- Prevents duplicate enrollments for the same course

---

#### 3. **Payment** (Updated)
Now links to specific course enrollment:

```python
+ enrollment: ForeignKey(StudentCourseEnrollment, nullable)
```

---

## Frontend Changes

### Registration Form Flow (products.html)

#### Step 1: Course Selection
User selects one of:
- **"Oncology Esthetics Certificate"** - Full program
- **"Pre-Certificate Bridge Course"** - For those without certification

#### Step 2: Conditional Prerequisite Check
**If Oncology Certificate selected:**
- Show: "Do you have the above-mentioned qualifications?"
- Option Yes → Require proof upload (PDF/JPG/PNG, max 5MB)
- Option No → Show bridge course suggestion

**If Bridge Course selected:**
- Skip prerequisite questions
- No proof required

#### Step 3: Contact Information
- Full Name
- Email Address  
- Contact Number

### Form Validation Logic
- **Course selection required:** Must select a course
- **Oncology certificate:** If selected, must answer prerequisite question
- **Proof upload:** If "Yes" to prerequisite, file is mandatory
- **File validation:** PDF/JPG/PNG only, max 5MB

---

## Backend Changes

### API Endpoint: `/api/register/` (POST)

**Request Parameters:**
```javascript
{
  name: string,           // Required
  email: string,          // Required
  contact: string,        // Required
  course: string,         // Required - "Oncology Esthetics Certificate" OR "Pre-Certificate Bridge Course"
  hasQualification: "yes"|"no",  // Required for Oncology, ignored for Bridge
  proof: File             // Required if hasQualification="yes"
}
```

**Response (Success):**
```json
{
  "status": "ok",
  "id": 5,
  "registration_id": "REG-20250101-000005",
  "enrollment_id": 12,
  "message": "Registration for [Course Name] successful!"
}
```

**Behavior:**
1. ✅ If student email exists → Get or create registration
2. ✅ Check if already enrolled in this specific course → Prevent duplicate
3. ✅ Create StudentCourseEnrollment record
4. ✅ Store proof (if provided)
5. ✅ Send admin & student notification emails

---

## Multi-Course Payment Selection

When a student has multiple course enrollments and accesses the payment portal:

### Payment Portal Features
- Display all enrolled courses
- Allow selection of which course to pay for
- Link payment to specific enrollment via Payment.enrollment FK

### Example Flow
1. Student registers for **Oncology Certificate** (has prerequisite)
2. Later, same student registers for **Bridge Course**
3. On payment portal:
   - Shows both courses
   - Student selects which one to pay for
   - Payment is tracked per course

---

## Migration Info

### Latest Migration
- **File:** `core/migrations/0007_remove_registration_auto_bridge_and_more.py`
- **Applied:** ✅

### Changes:
- Removed: `course`, `auto_bridge`, `proof*` fields from Registration
- Created: `StudentCourseEnrollment` model
- Added: `enrollment` FK to Payment model

---

## Admin Interface Updates

### Registration Admin
- List display: name, email, contact, created_at
- No longer shows course/auto_bridge

### StudentCourseEnrollment Admin (NEW)
- List display: registration, course_name, has_prerequisite, enrollment_status, enrolled_at
- Filterable by: course_name, enrollment_status
- Collapsible proof section

---

## Usage Examples

### Example 1: Student with Certificate
1. Selects: **"Oncology Esthetics Certificate"**
2. Answers: **"Yes, I have a certificate"**
3. Uploads: Proof PDF
4. Result: Enrolled in Oncology Certificate immediately

### Example 2: Student without Certificate
1. Selects: **"Oncology Esthetics Certificate"**
2. Answers: **"No, I don't have prerequisites"**
3. No file upload
4. Suggestion: Bridge Course recommended
5. Later: Student can register again for Bridge Course

### Example 3: Multiple Courses
1. First registration: Bridge Course
2. Second registration: Oncology Certificate (same email)
3. Payment portal: Choose which to pay for first

---

## Testing Checklist

- [ ] Register with certificate (proof upload)
- [ ] Register without certificate (bridge course)
- [ ] Register same email for second course
- [ ] Verify error on duplicate course enrollment
- [ ] Check admin interface shows all enrollments
- [ ] Verify payment links to correct enrollment
- [ ] Test file upload validation (type & size)
- [ ] Confirm emails sent to admin & student

---

## Notes for Future Development

### Payment Portal Enhancement
- Need to update payment selection view to show all enrollments
- Link Payment.enrollment field in checkout flow

### Certificate Issuance
- Track completion per course enrollment
- Issue certificates upon course completion

### Admin Workflows
- View student's all enrollments at a glance
- Update enrollment status (pending → approved → in_progress → completed)
