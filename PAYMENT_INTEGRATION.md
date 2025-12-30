# Payment Portal Integration Guide

## Overview
When students have registered for multiple courses, the payment portal needs to allow them to choose which course to pay for.

## Key Implementation Points

### 1. Student Login - Fetch All Enrollments

When a student logs in with their Registration ID, fetch all their course enrollments:

```python
# In payment views
from core.models import Registration, StudentCourseEnrollment

def student_dashboard(request):
    """Show student their enrollments and payment options"""
    registration_id = request.session.get('registration_id')  # Get from login
    
    try:
        registration = Registration.objects.get(registration_id=registration_id)
        enrollments = registration.course_enrollments.all()
        
        # Get outstanding payments (not completed)
        payments = registration.payments.filter(status__in=['pending', 'processing'])
        
        context = {
            'registration': registration,
            'enrollments': enrollments,
            'pending_payments': payments,
        }
        return render(request, 'payments/student_dashboard.html', context)
    except Registration.DoesNotExist:
        return redirect('student-login')
```

### 2. HTML Template - Show Available Courses

```html
<!-- templates/payments/student_dashboard.html -->
<h3>Your Enrolled Courses</h3>

{% if enrollments %}
    <div class="courses-list">
        {% for enrollment in enrollments %}
            <div class="course-card">
                <h5>{{ enrollment.course_name }}</h5>
                <p>Status: <span class="badge bg-{{ enrollment.get_status_color }}">
                    {{ enrollment.get_enrollment_status_display }}
                </span></p>
                
                {% if enrollment.has_prerequisite %}
                    <p><i class="lni lni-checkmark-circle"></i> Has prerequisite verified</p>
                {% else %}
                    <p><i class="lni lni-alert-circle"></i> Needs bridge course first</p>
                {% endif %}
                
                <!-- Check if already paid -->
                {% if enrollment.payments.filter|status__exact:"completed" %}
                    <p class="text-success">✓ Payment Complete</p>
                {% else %}
                    <a href="{% url 'payment-select-course' enrollment_id=enrollment.id %}" 
                       class="btn btn-primary">Proceed to Payment</a>
                {% endif %}
            </div>
        {% endfor %}
    </div>
{% else %}
    <p>You have no active course enrollments.</p>
{% endif %}
```

### 3. Course Selection for Payment

```python
# In core/views.py (payment flow)

@csrf_exempt
def select_payment_course(request, enrollment_id):
    """Allow student to select which course to pay for"""
    
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    
    try:
        enrollment = StudentCourseEnrollment.objects.get(id=enrollment_id)
        course_price = CoursePrice.objects.get(course_name=enrollment.course_name)
        
        context = {
            'enrollment': enrollment,
            'course': enrollment.course_name,
            'price': course_price.price_cad,
            'registration': enrollment.registration,
        }
        
        return render(request, 'payments/payment_select_amount.html', context)
    
    except (StudentCourseEnrollment.DoesNotExist, CoursePrice.DoesNotExist):
        return JsonResponse({'error': 'Course not found'}, status=404)


def initiate_payment(request):
    """Create payment record linked to specific enrollment"""
    
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    
    enrollment_id = request.POST.get('enrollment_id')
    payment_amount = request.POST.get('payment_amount')
    
    try:
        enrollment = StudentCourseEnrollment.objects.get(id=enrollment_id)
        course_price = CoursePrice.objects.get(course_name=enrollment.course_name)
        registration = enrollment.registration
        
        # Create Payment record linked to enrollment
        payment = Payment.objects.create(
            registration=registration,
            enrollment=enrollment,  # KEY: Link to specific enrollment
            student_id=registration.registration_id,
            course_name=enrollment.course_name,
            total_price_cad=course_price.price_cad,
            payment_amount_cad=Decimal(payment_amount),
            tax_amount=Decimal(0),  # Calculate based on your rules
            final_amount_cad=Decimal(payment_amount),
        )
        
        # Proceed with Stripe payment
        stripe_processor = StripePaymentProcessor()
        payment_intent = stripe_processor.create_payment_intent(
            amount_cents=int(payment.final_amount_cad * 100),
            student_name=registration.name,
            student_email=registration.email,
            payment_id=payment.id,
        )
        
        payment.stripe_payment_intent_id = payment_intent.id
        payment.save()
        
        return JsonResponse({
            'status': 'ok',
            'payment_intent_id': payment_intent.id,
            'client_secret': payment_intent.client_secret,
        })
    
    except (StudentCourseEnrollment.DoesNotExist, CoursePrice.DoesNotExist):
        return JsonResponse({'error': 'Invalid enrollment'}, status=400)
```

### 4. URL Configuration

Add these URLs to `core/urls.py`:

```python
from . import views

urlpatterns = [
    # ... existing URLs ...
    
    # Payment flows
    path('payment/dashboard/', views.student_dashboard, name='student-dashboard'),
    path('payment/select/<int:enrollment_id>/', views.select_payment_course, name='payment-select-course'),
    path('payment/initiate/', views.initiate_payment, name='payment-initiate'),
    path('payment/webhook/', views.stripe_webhook, name='stripe-webhook'),
]
```

### 5. Model Enhancement - Display Methods

Add these helper methods to StudentCourseEnrollment:

```python
# In core/models.py

class StudentCourseEnrollment(models.Model):
    # ... existing fields ...
    
    def get_enrollment_status_display(self):
        """Human-readable status"""
        status_map = {
            'pending': 'Pending Review',
            'approved': 'Approved',
            'in_progress': 'In Progress',
            'completed': 'Completed',
        }
        return status_map.get(self.enrollment_status, self.enrollment_status)
    
    def get_status_color(self):
        """Bootstrap color for status badge"""
        color_map = {
            'pending': 'warning',
            'approved': 'info',
            'in_progress': 'primary',
            'completed': 'success',
        }
        return color_map.get(self.enrollment_status, 'secondary')
    
    def has_paid(self):
        """Check if this enrollment has a completed payment"""
        return self.payments.filter(status='completed').exists()
    
    @property
    def payment_status(self):
        """Get latest payment status"""
        latest_payment = self.payments.first()
        return latest_payment.status if latest_payment else 'unpaid'
```

### 6. Admin Enhancement - Show Payments

Update PaymentAdmin to show enrollment:

```python
# In core/admin.py

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'invoice_number', 
        'student_id', 
        'course_name',
        'get_enrollment_status',  # NEW
        'payment_amount_cad', 
        'status', 
        'completed_at'
    )
    
    def get_enrollment_status(self, obj):
        """Show enrollment status if linked"""
        if obj.enrollment:
            return f"{obj.enrollment.enrollment_status}"
        return "—"
    
    get_enrollment_status.short_description = 'Enrollment Status'
```

---

## Flow Diagram

```
Student Logs In
    ↓
Fetch Registration (by ID)
    ↓
Display All Enrollments (course_enrollments.all())
    ↓
Student Clicks "Pay for [Course]"
    ↓
Route to: /payment/select/{enrollment_id}/
    ↓
Show Course Details & Price
    ↓
Student Selects Amount & Proceeds
    ↓
POST to /payment/initiate/
    ↓
Create Payment with enrollment FK
    ↓
Create Stripe PaymentIntent
    ↓
Return client_secret for frontend
    ↓
Stripe Checkout Modal
    ↓
Payment Success
    ↓
Update Payment & Enrollment statuses
    ↓
Send confirmation email
```

---

## Testing the Multi-Course Payment

### Test Case 1: Single Course
1. Register for Oncology Certificate
2. Go to payment
3. Should see only that course
4. Complete payment
5. Verify Payment.enrollment points to correct enrollment

### Test Case 2: Multiple Courses
1. Register for Bridge Course
2. Register for Oncology Certificate (same email)
3. Go to payment
4. Should see both courses with selection
5. Pay for Bridge Course first
6. Later, pay for Oncology Certificate
7. Verify both have separate Payment records linked via enrollment

### Test Case 3: Status Updates
1. Register & pay for course
2. Admin updates enrollment_status to "approved"
3. Student dashboard should reflect status
4. Admin can see all payments per enrollment

---

## Current TODO Items

- [ ] Create student_dashboard view
- [ ] Create select_payment_course view
- [ ] Update initiate_payment to link enrollment
- [ ] Add helper methods to StudentCourseEnrollment
- [ ] Update payment templates to show course selector
- [ ] Update Stripe webhook handler to update enrollment status on payment completion
- [ ] Add tests for multi-course payment flow
- [ ] Update admin interface as shown above
