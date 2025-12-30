from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from .models import Registration, StudentCourseEnrollment, CoursePrice, Payment, PaymentInvoice


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
	list_display = ('name', 'email', 'contact', 'created_at')
	list_filter = ('created_at', 'updated_at')
	search_fields = ('name', 'email', 'contact')
	readonly_fields = ('registration_id', 'created_at', 'updated_at')


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


@admin.register(CoursePrice)
class CoursePriceAdmin(admin.ModelAdmin):
	list_display = ('course_name', 'price_cad', 'created_at', 'updated_at')
	search_fields = ('course_name',)
	list_filter = ('created_at', 'updated_at')
	readonly_fields = ('created_at', 'updated_at')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'student_id', 'course_name', 'payment_amount_cad', 'status_display', 'completed_at')
    list_filter = ('status', 'created_at', 'payment_method')
    search_fields = ('student_id', 'invoice_number', 'course_name', 'registration__email')
    readonly_fields = ('registration', 'student_id', 'transaction_id', 'invoice_number', 'created_at', 'updated_at', 'completed_at')
    actions = ['download_invoice_action']
    
    fieldsets = (
        ('Student Information', {
            'fields': ('registration', 'student_id')
        }),
        ('Course & Payment Details', {
            'fields': ('course_name', 'enrollment', 'total_price_cad', 'payment_amount_cad', 'tax_amount', 'final_amount_cad')
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
    
    def status_display(self, obj):
        """Display status with color coding"""
        colors = {
            'completed': '#28a745',  # Green
            'pending': '#ffc107',    # Yellow
            'failed': '#dc3545',     # Red
            'cancelled': '#6c757d'   # Gray
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def download_invoice_action(self, request, queryset):
        """Admin action to download selected invoices"""
        if queryset.count() == 1:
            payment = queryset.first()
            try:
                html = self._generate_invoice_html(payment)
                response = HttpResponse(html, content_type='text/html')
                response['Content-Disposition'] = f'attachment; filename="Invoice_{payment.invoice_number}.html"'
                return response
            except Exception as e:
                self.message_user(request, f'Error generating invoice: {str(e)}', level='ERROR')
        else:
            self.message_user(request, 'Please select only one payment to download.', level='WARNING')
    download_invoice_action.short_description = "📥 Download selected payment invoice"
    
    def _generate_invoice_html(self, payment):
        """Generate invoice HTML"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .invoice-container {{ max-width: 900px; margin: 0 auto; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .invoice-details {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }}
                .detail-box {{ border: 1px solid #ddd; padding: 15px; }}
                .label {{ font-weight: bold; color: #333; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th {{ background-color: #f5f5f5; padding: 10px; text-align: left; border-bottom: 2px solid #ddd; }}
                td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
                .total-row {{ font-weight: bold; background-color: #f9f9f9; }}
                .status-badge {{ 
                    padding: 5px 10px; 
                    border-radius: 5px; 
                    color: white;
                    font-weight: bold;
                }}
                .status-completed {{ background-color: #28a745; }}
                .status-pending {{ background-color: #ffc107; color: #333; }}
                .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #666; }}
            </style>
        </head>
        <body>
            <div class="invoice-container">
                <div class="header">
                    <h1>INVOICE</h1>
                    <p>Invoice Number: <strong>{payment.invoice_number}</strong></p>
                </div>
                
                <div class="invoice-details">
                    <div class="detail-box">
                        <div><span class="label">Student Name:</span> {payment.registration.name}</div>
                        <div><span class="label">Email:</span> {payment.registration.email}</div>
                        <div><span class="label">Contact:</span> {payment.registration.contact}</div>
                        <div><span class="label">Registration ID:</span> {payment.registration.registration_id}</div>
                    </div>
                    
                    <div class="detail-box">
                        <div><span class="label">Course:</span> {payment.course_name}</div>
                        <div><span class="label">Payment Date:</span> {payment.completed_at.strftime('%Y-%m-%d %H:%M') if payment.completed_at else 'Pending'}</div>
                        <div><span class="label">Payment Method:</span> {payment.get_payment_method_display()}</div>
                        <div><span class="label">Status:</span> <span class="status-badge status-{payment.status}">{payment.get_status_display()}</span></div>
                    </div>
                </div>
                
                <table>
                    <tr>
                        <th>Description</th>
                        <th style="text-align: right;">Amount</th>
                    </tr>
                    <tr>
                        <td>Course Fee</td>
                        <td style="text-align: right;">${payment.total_price_cad:.2f}</td>
                    </tr>
                    <tr>
                        <td>Payment Amount</td>
                        <td style="text-align: right;">${payment.payment_amount_cad:.2f}</td>
                    </tr>
                    <tr>
                        <td>Tax (5%)</td>
                        <td style="text-align: right;">${payment.tax_amount:.2f}</td>
                    </tr>
                    <tr class="total-row">
                        <td>Total Amount Paid</td>
                        <td style="text-align: right;">${payment.final_amount_cad:.2f}</td>
                    </tr>
                </table>
                
                <div class="footer">
                    <p>This is an official payment receipt for {payment.registration.name}</p>
                    <p>Transaction ID: {payment.transaction_id}</p>
                    <p>Generated on: {payment.completed_at.strftime('%Y-%m-%d %H:%M:%S') if payment.completed_at else 'N/A'}</p>
                </div>
            </div>
        </body>
        </html>
        """


@admin.register(PaymentInvoice)
class PaymentInvoiceAdmin(admin.ModelAdmin):
    list_display = ('payment', 'generated_at')
    search_fields = ('payment__invoice_number',)
    readonly_fields = ('payment', 'generated_at')

