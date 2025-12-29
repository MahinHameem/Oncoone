from django.urls import path
from . import views

urlpatterns = [
    # Admin registrations API
    path('admin/registrations/', views.registrations_list, name='admin-registrations-list'),
    path('admin/registrations/<int:pk>/', views.registration_detail, name='admin-registrations-detail'),
    path('admin/registrations/<int:pk>/download/', views.download_proof, name='admin-registrations-download'),
    
    # Admin pages
    path('admin/students/', views.admin_students_page, name='admin-students-page'),
    path('admin/courses/', views.admin_courses_page, name='admin-courses-page'),
    
    # Authentication
    path('admin/login/', views.staff_login, name='staff-login'),
    path('admin/logout/', views.staff_logout, name='staff-logout'),
    
    # Payment Portal Routes (now under /api/ in main urls.py)
    path('payment/', views.payment_portal_home, name='payment-portal-home'),
    path('payment/select-course/<int:student_id>/', views.payment_select_course, name='payment-select-course'),
    path('payment/summary/<int:student_id>/', views.payment_summary, name='payment-summary'),
    path('payment/card-entry/<int:student_id>/', views.payment_card_entry, name='payment-card-entry'),
    path('payment/otp-verification/<int:payment_id>/', views.payment_otp_verification_page, name='payment-otp-verification'),
    path('payment/success/<int:payment_id>/', views.payment_success, name='payment-success'),
    path('payment/cancelled/<int:student_id>/', views.payment_cancelled, name='payment-cancelled'),
    
    # Payment API Routes (now under /api/ in main urls.py)
    path('payment/verify-student/', views.payment_verify_student, name='api-payment-verify-student'),
    path('payment/calculate-tax/', views.payment_calculate_tax, name='api-payment-calculate-tax'),
    path('payment/process/', views.process_payment, name='api-payment-process'),
    path('payment/create-and-send-otp/', views.create_payment_and_send_otp, name='api-create-payment-otp'),
    path('payment/verify-otp/', views.verify_payment_otp, name='api-verify-payment-otp'),
]
