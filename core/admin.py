from django.contrib import admin
from .models import Registration, CoursePrice, Payment, PaymentInvoice


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'contact', 'course', 'auto_bridge', 'created_at')
    list_filter = ('auto_bridge', 'created_at')
    search_fields = ('name', 'email', 'contact', 'course')


@admin.register(CoursePrice)
class CoursePriceAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'price_cad', 'created_at', 'updated_at')
    search_fields = ('course_name',)
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'student_id', 'course_name', 'payment_amount_cad', 'status', 'completed_at')
    list_filter = ('status', 'created_at', 'payment_method')
    search_fields = ('student_id', 'invoice_number', 'course_name')
    readonly_fields = ('registration', 'student_id', 'transaction_id', 'invoice_number', 'created_at', 'updated_at', 'completed_at')
    fieldsets = (
        ('Student Information', {
            'fields': ('registration', 'student_id')
        }),
        ('Course & Payment Details', {
            'fields': ('course_name', 'total_price_cad', 'payment_amount_cad', 'tax_amount', 'final_amount_cad')
        }),
        ('Payment Method', {
            'fields': ('payment_method', 'card_holder_name', 'card_last_four')
        }),
        ('Transaction Details', {
            'fields': ('status', 'transaction_id', 'invoice_number')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        })
    )


@admin.register(PaymentInvoice)
class PaymentInvoiceAdmin(admin.ModelAdmin):
    list_display = ('payment', 'generated_at')
    search_fields = ('payment__invoice_number',)
    readonly_fields = ('payment', 'generated_at')

