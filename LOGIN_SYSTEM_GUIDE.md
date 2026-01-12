# Login System Architecture

## Current Configuration

### ✅ PAYMENT PORTAL (Primary for Students)
**URL:** `/api/payment/`  
**Authentication:** Registration Number (ON26-XXXXXX)  
**Purpose:** Student payments and course enrollment

**Login Flow:**
1. Student enters Registration Number: `ON26-370761`
2. System verifies and shows their courses
3. Student selects course and makes payment

---

### ✅ ADMIN LOGIN (Staff Only)
**URL:** `/admin/login/`  
**Authentication:** Username + Password  
**Purpose:** Admin and staff management

**Login Flow:**
1. Staff enters username and password
2. Access to admin panel
3. Manage students, courses, payments

---

### ℹ️ STUDENT LOGIN (Legacy)
**URL:** `/api/student/login/`  
**Status:** Legacy system (kept for backward compatibility)  
**Note:** Not used in current workflow

---

## Recommended Usage

### For Students
- **ONLY use:** `/api/payment/` with Registration Number (ON26-XXXXXX)
- Example: `ON26-370761`

### For Admin/Staff
- **ONLY use:** `/admin/login/` with username and password

---

## System Separation

| System | URL | Who Uses | Auth Method |
|--------|-----|----------|-------------|
| Payment Portal | `/api/payment/` | Students | Registration Number (ON26-XXXXXX) |
| Admin Panel | `/admin/` | Staff | Username + Password |
| Student Login | `/api/student/login/` | Legacy | Student ID |

---

**Important:** Keep these systems separate. Students use Registration Number for payments. Admin/staff use credentials for admin panel.

---
**Last Updated:** January 12, 2026
