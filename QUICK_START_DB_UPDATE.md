# Quick Start - Database Updates

## What Changed?

### 1. Professional Registration Numbers ✓
Students now get registration numbers in format: **ON26-0001**
- ON = OncoOne
- 26 = Year (2026, 2027, etc.)
- 0001 = Sequential number

### 2. Unique Student Passwords ✓
Every student gets a unique 10-character password:
- Auto-generated on registration
- Mix of letters, numbers, symbols
- Example: `aB3!xY9$kL`

### 3. Separate Course Table ✓
Courses are now managed in their own table:
- Add/edit courses easily in admin
- Set prices per course
- Manage multiple course types

### 4. Many-to-Many Enrollments ✓
- 1 student can enroll in multiple courses
- 1 course can have multiple students
- Proper relational database structure

## Quick Setup (3 Steps)

### Step 1: Apply Database Changes
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 2: Create Sample Courses
```bash
python seed_courses.py
```

### Step 3: Update Existing Students (if any)
```bash
python update_existing_registrations.py
```

## What You'll See

### Admin Students Page
```
Reg. Number | Name      | Email           | Password      | Course
------------|-----------|-----------------|---------------|------------------
ON26-0001   | John Doe  | john@email.com  | aB3!xY9$kL   | Oncology Esthetics
ON26-0002   | Jane Smith| jane@email.com  | Zx7@mN2^pQ   | Bridge Course
```

### Django Admin Panel
- **Courses** - Manage all courses, prices, codes
- **Student Registrations** - See registration numbers & passwords
- **Enrollments** - Link students to courses

## New Features

✓ Professional registration IDs (ON26-0001)  
✓ Unique 10-character passwords  
✓ Year-based numbering (ON27-XXXX in 2027)  
✓ Centralized course management  
✓ Multiple course enrollments per student  
✓ Auto-generated on registration  

## Files Created

- `core/migrations/0010_course_structure_update.py` - Database schema
- `core/migrations/0011_populate_registration_numbers_and_courses.py` - Data migration
- `seed_courses.py` - Create sample courses
- `update_existing_registrations.py` - Update existing students
- `DATABASE_STRUCTURE_UPDATE.md` - Full documentation

## Files Modified

- `core/models.py` - Added Course model, updated Registration & Enrollment
- `core/views.py` - Updated to use registration_number instead of registration_id
- `core/admin.py` - Added Course admin, updated Registration display
- `templates/admin/students.html` - Shows registration number & password

## Testing

### Test New Registration
1. Register a new student
2. Check they get ON26-XXXX number
3. Check they have unique password
4. See in admin panel

### Test Multiple Courses
1. Create 2+ courses in admin
2. Enroll 1 student in multiple courses
3. Verify relationships work

## Questions?

See `DATABASE_STRUCTURE_UPDATE.md` for full details!

---
**Status:** ✓ Ready to Use  
**Version:** 2.0  
**Date:** January 12, 2026
