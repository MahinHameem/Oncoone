# Database Structure Update - Student Registration System

## Overview
This update restructures the database to have a proper relational schema with separate tables for students, courses, and enrollments, plus adds professional registration numbers and unique passwords for students.

## Changes Made

### 1. New Course Model
Created a dedicated `Course` model to manage all course types:

**Fields:**
- `course_name` - Full course name (unique)
- `course_code` - Short code identifier (unique, e.g., "OEC01", "BRIDGE01")
- `description` - Course description
- `price_cad` - Course price in CAD
- `duration_weeks` - Course duration in weeks
- `requires_prerequisite` - Whether course requires proof of certification
- `is_active` - Active/inactive status
- `created_at` / `updated_at` - Timestamps

**Benefits:**
- Centralized course management
- Easy to add/edit courses without code changes
- Supports multiple course types
- Proper pricing management

### 2. Updated Registration Model (Student Details)

**New Fields:**
- `registration_number` - Professional format: **ON26-0001** (unique, indexed)
  - ON = OncoOne prefix
  - 26 = Year (2026), auto-updates based on registration year
  - 0001 = Sequential 4-digit number
  - Example: Student registered in 2027 gets ON27-0001
  
- `student_password` - 10-character unique password
  - Auto-generated on registration
  - Contains mix of uppercase, lowercase, digits, and special characters
  - Guaranteed unique across all students
  - Stored securely in database

**Registration Number Format:**
```
ON{YY}-{XXXX}
│  │   └── Sequential number (0001-9999)
│  └────── Year suffix (26 for 2026, 27 for 2027, etc.)
└───────── OncoOne prefix
```

### 3. Updated StudentCourseEnrollment Model

**Changes:**
- Added `course` foreign key to Course model (many-to-many relationship)
- Kept `course_name` for backward compatibility (auto-populated)
- **Many-to-Many Relationship:**
  - 1 student can enroll in many courses
  - 1 course can have many students enrolled

**Unique Constraint:**
- Each student can only enroll once per course (prevents duplicates)

### 4. Removed CoursePrice Model
- Replaced by Course model
- Price now stored directly in Course model
- Cleaner data structure

## Database Migrations

### Migration Files Created:
1. **0010_course_structure_update.py**
   - Creates Course model
   - Adds registration_number to Registration
   - Adds course foreign key to StudentCourseEnrollment
   - Removes CoursePrice model

2. **0011_populate_registration_numbers_and_courses.py**
   - Generates registration numbers for existing students
   - Creates Course records from existing enrollments
   - Links enrollments to courses

## How to Apply Changes

### Step 1: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 2: Seed Sample Courses (Optional)
```bash
python seed_courses.py
```

This will create 4 sample courses:
- Oncology Esthetics Certificate (OEC01) - $2500
- Pre-Certificate Bridge Course (BRIDGE01) - $1500
- Advanced Oncology Skincare (AOS01) - $1800
- Oncology Makeup Techniques (OMT01) - $1200

### Step 3: Check Admin Panel
Navigate to Django admin to manage:
- **Courses** - Add/edit/deactivate courses
- **Student Registrations** - View registration numbers and passwords
- **Course Enrollments** - See which students are enrolled in which courses

## Admin Interface Updates

### Students Page
Now displays:
- **Registration Number** - ON26-0001 format (bold)
- **Full Name**
- **Contact Number**
- **Email**
- **Password** - 10-character unique password (monospace font)
- **Course Type** - All enrolled courses
- **Payment details** (Fee, Paid, Balance)
- **Status & Actions**

### Django Admin Panel
**Registration Admin:**
- Shows registration_number and student_password in list view
- Both fields are read-only (auto-generated)
- Searchable by registration number

**Course Admin:**
- Full course management interface
- Set prices, duration, prerequisites
- Activate/deactivate courses

**Enrollment Admin:**
- Links students to courses
- Track enrollment status
- Manage prerequisite proofs

## API Changes

### Registration Endpoint Response
Now includes:
```json
{
  "id": 1,
  "registration_number": "ON26-0001",
  "student_password": "aB3!xY9$kL",
  "name": "John Doe",
  "email": "john@example.com",
  "contact": "+1234567890",
  ...
}
```

### Students List API
Returns registration_number and student_password for each student.

## Password Generation

**Security Features:**
- 10 characters long
- Mix of uppercase letters, lowercase letters, digits, and special characters
- **Guaranteed unique** - checks database before assigning
- Auto-generated on student registration
- Displayed in admin panel for staff access
- Can be used for student portal login

**Example passwords:**
- `aB3!xY9$kL`
- `Zx7@mN2^pQ`
- `K9#vL4&wR8`

## Registration Number Generation

**Algorithm:**
1. Get current year (e.g., 2026)
2. Extract last 2 digits (26)
3. Find highest existing number for that year (e.g., ON26-0015)
4. Increment by 1 (ON26-0016)
5. If no registrations for year, start at 0001

**Features:**
- Resets numbering each year (ON26-9999 → ON27-0001)
- Guaranteed unique across all time
- Easy to identify registration year
- Professional appearance

## Example Usage

### Creating a New Course (Django Admin)
1. Go to Admin → Courses → Add Course
2. Fill in:
   - Course Name: "Oncology Esthetics Certificate"
   - Course Code: "OEC01"
   - Price: 2500.00
   - Duration: 12 weeks
   - Requires Prerequisite: Yes
3. Save

### Enrolling a Student
1. Student registers via website
2. System automatically:
   - Creates Registration with ON26-XXXX number
   - Generates unique 10-char password
   - Creates StudentCourseEnrollment linked to Course
3. Admin can see:
   - Registration Number: ON26-0001
   - Password: aB3!xY9$kL
   - Enrolled Course: Oncology Esthetics Certificate

### Student Can Enroll in Multiple Courses
```python
# Student ON26-0001 enrolls in multiple courses
student = Registration.objects.get(registration_number="ON26-0001")

# Enroll in first course
course1 = Course.objects.get(course_code="OEC01")
StudentCourseEnrollment.objects.create(
    registration=student,
    course=course1,
    has_prerequisite=True
)

# Enroll in second course
course2 = Course.objects.get(course_code="BRIDGE01")
StudentCourseEnrollment.objects.create(
    registration=student,
    course=course2,
    has_prerequisite=False
)

# Student ON26-0001 is now enrolled in 2 courses
```

## Testing

### Test Registration Number Generation
```python
from core.models import Registration

# Create test registrations
reg1 = Registration.objects.create(name="Test 1", email="test1@example.com", contact="123")
print(reg1.registration_number)  # ON26-0001

reg2 = Registration.objects.create(name="Test 2", email="test2@example.com", contact="456")
print(reg2.registration_number)  # ON26-0002
```

### Test Password Uniqueness
```python
# Create 10 students
passwords = set()
for i in range(10):
    reg = Registration.objects.create(
        name=f"Student {i}",
        email=f"student{i}@test.com",
        contact=f"{i}000"
    )
    passwords.add(reg.student_password)

# All passwords should be unique
assert len(passwords) == 10
print("✓ All passwords are unique!")
```

## Backward Compatibility

**Preserved:**
- `course_name` field in StudentCourseEnrollment (auto-synced from Course)
- Existing payment system continues to work
- All existing API endpoints maintained

**Migration Notes:**
- Existing students will get registration numbers assigned (ON26-0001, ON26-0002, etc.)
- Existing course names will be converted to Course records
- Existing enrollments will be linked to new Course records

## Benefits

1. **Professional Appearance**
   - Registration numbers look official (ON26-0001)
   - Easy to communicate and remember

2. **Better Organization**
   - Courses managed centrally
   - Clear student-course relationships
   - Proper many-to-many structure

3. **Security**
   - Unique passwords for each student
   - Can be used for portal access
   - No duplicate passwords possible

4. **Scalability**
   - Easy to add new courses
   - Supports unlimited students
   - Handles multiple enrollments per student

5. **Year Tracking**
   - Registration numbers show enrollment year
   - Easy to generate yearly reports
   - Automatic year rollover

## Support

For questions or issues:
1. Check Django admin panel for data
2. Review migration files in `core/migrations/`
3. Run `python manage.py check` to verify setup
4. Check logs for errors

---

**Updated:** January 12, 2026
**Version:** 2.0
**Status:** ✓ Implemented and Ready
