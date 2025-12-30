# Code Changes Summary

## Files Modified

### 1. core/models.py

#### REMOVED from Registration:
```python
# These fields are no longer on Registration
- course = models.CharField(max_length=255)
- auto_bridge = models.BooleanField(default=False)
- proof = models.FileField(upload_to='proofs/', blank=True, null=True)
- proof_name = models.CharField(max_length=255, blank=True, null=True)
- proof_mime = models.CharField(max_length=100, blank=True, null=True)
- proof_data = models.BinaryField(blank=True, null=True)
```

#### ADDED to Registration:
```python
def get_enrolled_courses(self):
    """Get all courses this student is enrolled in"""
    return StudentCourseEnrollment.objects.filter(registration=self)
```

#### NEW MODEL: StudentCourseEnrollment
```python
class StudentCourseEnrollment(models.Model):
    """Track each course enrollment for a student (allows multiple courses per student)"""
    
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name='course_enrollments')
    course_name = models.CharField(max_length=255)
    has_prerequisite = models.BooleanField(default=True)
    
    # Proof of prerequisite
    proof = models.FileField(upload_to='proofs/', blank=True, null=True)
    proof_name = models.CharField(max_length=255, blank=True, null=True)
    proof_mime = models.CharField(max_length=100, blank=True, null=True)
    proof_data = models.BinaryField(blank=True, null=True)
    
    enrollment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
        ],
        default='pending'
    )
    
    enrolled_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['registration', 'course_name']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.registration.email} - {self.course_name}"
```

#### UPDATED Payment:
```python
# Added field
enrollment = models.ForeignKey(
    StudentCourseEnrollment, 
    on_delete=models.CASCADE, 
    related_name='payments',
    blank=True,
    null=True
)
```

---

### 2. core/views.py

#### UPDATED register_view function:
**Old signature:**
```python
@csrf_exempt
def register_view(request):
    # ... old code that created Registration with course field
```

**New signature:**
```python
@csrf_exempt
def register_view(request):
    """Handle course registration - supports multiple courses per student"""
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)

    try:
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        contact = request.POST.get('contact', '').strip()
        course_name = request.POST.get('course', '').strip()
        has_prerequisite = request.POST.get('hasQualification', 'yes').lower() in ('yes', '1', 'true')
        proof = request.FILES.get('proof')

        # ... validation code ...

        # Get or create registration
        reg, created = Registration.objects.get_or_create(
            email=email,
            defaults={'name': name, 'contact': contact}
        )

        # Check if already enrolled in this course
        if StudentCourseEnrollment.objects.filter(
            registration=reg, 
            course_name=course_name
        ).exists():
            return JsonResponse({
                'status': 'error',
                'error': f'You are already registered for {course_name}.'
            }, status=400)

        # Create enrollment (not registration)
        enrollment = StudentCourseEnrollment.objects.create(
            registration=reg,
            course_name=course_name,
            has_prerequisite=has_prerequisite,
            proof=proof if proof else None,
            proof_name=proof_name,
            proof_mime=proof_mime,
            proof_data=proof_bytes,
        )

        # ... email logic ...

        return JsonResponse({
            'status': 'ok',
            'id': reg.id,
            'registration_id': reg.registration_id,
            'enrollment_id': enrollment.id,
            'message': f'Registration for {course_name} successful!'
        })

    except Exception as e:
        print(f"Registration error: {e}")
        return JsonResponse({'status': 'error', 'error': str(e)}, status=500)
```

#### Updated import:
```python
# Old
from .models import Registration, Payment, CoursePrice, PaymentInvoice, PaymentOTP

# New
from .models import Registration, StudentCourseEnrollment, Payment, CoursePrice, PaymentInvoice, PaymentOTP
```

---

### 3. core/admin.py

#### UPDATED RegistrationAdmin:
```python
# Old
@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'contact', 'course', 'auto_bridge', 'created_at')
    list_filter = ('auto_bridge', 'created_at')
    search_fields = ('name', 'email', 'contact', 'course')

# New
@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'contact', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'email', 'contact')
    readonly_fields = ('registration_id', 'created_at', 'updated_at')
```

#### NEW StudentCourseEnrollmentAdmin:
```python
@admin.register(StudentCourseEnrollment)
class StudentCourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('registration', 'course_name', 'has_prerequisite', 'enrollment_status', 'enrolled_at')
    list_filter = ('course_name', 'has_prerequisite', 'enrollment_status', 'enrolled_at')
    search_fields = ('registration__email', 'registration__name', 'course_name')
    readonly_fields = ('enrolled_at', 'updated_at')
    fieldsets = (
        ('Student Information', {
            'fields': ('registration',)
        }),
        ('Course Details', {
            'fields': ('course_name', 'has_prerequisite', 'enrollment_status')
        }),
        ('Prerequisite Proof', {
            'fields': ('proof', 'proof_name', 'proof_mime'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('enrolled_at', 'updated_at')
        })
    )
```

#### Updated import:
```python
# Old
from .models import Registration, CoursePrice, Payment, PaymentInvoice

# New
from .models import Registration, StudentCourseEnrollment, CoursePrice, Payment, PaymentInvoice
```

---

### 4. templates/products.html

#### REMOVED elements:
```html
<!-- OLD: Hidden course field -->
<input type="hidden" name="course" id="courseField" value="Oncology Esthetics Certificate">
<input type="hidden" name="autoBridge" id="autoBridge" value="false">

<!-- OLD: Direct prerequisite questions without course selection -->
<div class="mb-3">
    <label class="form-label">Do you have the above-mentioned qualifications?...</label>
    ...
</div>
```

#### ADDED elements:
```html
<!-- NEW: Course selection -->
<div class="mb-3">
    <label class="form-label">Which course would you like to register for? <span class="required-star">*</span></label>
    <div class="form-check">
        <input class="form-check-input course-option" type="radio" name="course" id="courseOncology" 
               value="Oncology Esthetics Certificate" required>
        <label class="form-check-label" for="courseOncology">
            <strong>Oncology Esthetics Certificate</strong> (Full Program - Requires prerequisite)
        </label>
    </div>
    <div class="form-check">
        <input class="form-check-input course-option" type="radio" name="course" id="courseBridge" 
               value="Pre-Certificate Bridge Course">
        <label class="form-check-label" for="courseBridge">
            <strong>Pre-Certificate Bridge Course</strong> (For those without esthetics certification)
        </label>
    </div>
</div>

<!-- NEW: Conditional prerequisite container -->
<div class="mb-3" id="qualificationContainer" style="display:none;">
    <label class="form-label">Do you have the above-mentioned qualifications?...</label>
    ...
</div>
```

#### Updated JavaScript:
```javascript
// OLD: Simple radio change
qualYes.addEventListener('change', setForYes);
qualNo.addEventListener('change', setForNo);

// NEW: Course selection handling
courseOptions.forEach(option => {
    option.addEventListener('change', function() {
        if (this.value === 'Oncology Esthetics Certificate') {
            qualificationContainer.style.display = 'block';
            // Reset fields
        } else {
            qualificationContainer.style.display = 'none';
        }
    });
});

// NEW: Form submission with course validation
form.addEventListener('submit', async function(e) {
    // ... validation ...
    const selectedCourse = document.querySelector('.course-option:checked');
    if (!selectedCourse) {
        alert('Please select a course.');
        return;
    }
    // ... more validation ...
});
```

---

### 5. Migration File: core/migrations/0007_*.py

**Created automatically by Django:**
```python
migrations.RemoveField(
    model_name='registration',
    name='auto_bridge',
),
migrations.RemoveField(
    model_name='registration',
    name='course',
),
migrations.RemoveField(
    model_name='registration',
    name='proof',
),
migrations.RemoveField(
    model_name='registration',
    name='proof_data',
),
migrations.RemoveField(
    model_name='registration',
    name='proof_mime',
),
migrations.RemoveField(
    model_name='registration',
    name='proof_name',
),
migrations.CreateModel(
    name='StudentCourseEnrollment',
    fields=[
        ('id', models.BigAutoField(...)),
        ('course_name', models.CharField(max_length=255)),
        ('has_prerequisite', models.BooleanField(default=True)),
        ('proof', models.FileField(...)),
        ('proof_name', models.CharField(...)),
        ('proof_mime', models.CharField(...)),
        ('proof_data', models.BinaryField(...)),
        ('enrollment_status', models.CharField(...)),
        ('enrolled_at', models.DateTimeField(auto_now_add=True)),
        ('updated_at', models.DateTimeField(auto_now=True)),
        ('registration', models.ForeignKey(...)),
    ],
),
migrations.AddField(
    model_name='payment',
    name='enrollment',
    field=models.ForeignKey(..., null=True),
),
```

---

## Summary of Changes

| Component | What Changed |
|-----------|--------------|
| **Models** | Registration simplified, StudentCourseEnrollment created, Payment updated |
| **Views** | register_view now handles multiple courses, get_or_create instead of create |
| **Admin** | Updated RegistrationAdmin, added StudentCourseEnrollmentAdmin |
| **Frontend** | Added course selection, conditional prerequisite questions |
| **Database** | New table for enrollments, removed fields from registrations |

## Key Logic Changes

### Old Flow
```
POST /api/register/
  → Check unique email
  → Create Registration (one per email)
  → Return registration_id
```

### New Flow
```
POST /api/register/
  → Get or create Registration (by email)
  → Check for duplicate course enrollment
  → Create StudentCourseEnrollment
  → Return registration_id + enrollment_id
```

## Backward Compatibility

⚠️ **Breaking Changes:**
- Old registrations still have their data
- Can't query by registration.course anymore
- Must use registration.course_enrollments.all()

✅ **Migration Path:**
```python
# Old way (broken now)
reg = Registration.objects.get(email="jane@example.com")
course = reg.course  # AttributeError!

# New way
reg = Registration.objects.get(email="jane@example.com")
enrollments = reg.course_enrollments.all()
for enrollment in enrollments:
    print(enrollment.course_name)
```
