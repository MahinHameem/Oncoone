from django.shortcuts import render
from django.core.mail import EmailMessage
from django.conf import settings
from .speaking_session_form import SpeakingSessionForm
from .models import SpeakingSession
from django.db.models import Count

from .models import Payment

def index_view(request):
    """Serve the index.html homepage and handle speaking session form."""
    workshop_paid_count = Payment.objects.filter(
        course_name='Cancer Nutrition Workshop',
        status='completed'
    ).count()
    workshop_sold_out = workshop_paid_count >= 20

    form = SpeakingSessionForm()
    success_msg = None
    error_msg = None
    if request.method == 'POST' and request.POST.get('form_type') == 'speaking_session':
        form = SpeakingSessionForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # Save to database
            SpeakingSession.objects.create(
                name=data['name'],
                email=data['email'],
                phone=data['phone'],
                session_for=data['session_for'],
                session_type=data['session_type'],
                mode=data['mode'],
                date=data['date'],
                time=data['time'],
                participants=data.get('participants'),
                purpose=data['purpose'],
                notes=data['notes'],
            )
            # Compose admin email
            admin_subject = f"[Oncoone] New Speaking Session Booking from {data['name']}"
            admin_body = (
                f"A new speaking session has been booked.\n\n"
                f"Name: {data['name']}\n"
                f"Email: {data['email']}\n"
                f"Phone: {data['phone']}\n"
                f"Session For: {data['session_for']}\n"
                f"Session Type: {data['session_type']}\n"
                f"Mode: {data['mode']}\n"
                f"Preferred Date: {data['date']}\n"
                f"Preferred Time: {data['time']}\n"
                f"Participants: {data.get('participants') or '-'}\n"
                f"Purpose: {data['purpose']}\n"
                f"Notes: {data['notes']}\n"
            )
            admin_email = getattr(settings, 'SPEAKING_SESSION_ADMIN_EMAIL', settings.DEFAULT_FROM_EMAIL)
            try:
                EmailMessage(admin_subject, admin_body, settings.DEFAULT_FROM_EMAIL, [admin_email]).send(fail_silently=False)
                # Compose user confirmation email
                user_subject = "Your Speaking Session Booking with Oncoone"
                user_body = (
                    f"Dear {data['name']},\n\n"
                    "Thank you for booking a speaking session with Oncoone. We have received your request and will contact you soon to confirm the details.\n\n"
                    "Best regards,\nOncoone Team"
                )
                EmailMessage(user_subject, user_body, settings.DEFAULT_FROM_EMAIL, [data['email']]).send(fail_silently=True)
                success_msg = "Thank you! Your booking has been received. We will contact you soon."
                form = SpeakingSessionForm()  # Reset form
            except Exception as e:
                error_msg = "Sorry, there was an error sending your booking. Please try again later."
        else:
            error_msg = "Please correct the errors below."

    return render(request, 'index.html', {
        'workshop_sold_out': workshop_sold_out,
        'workshop_paid_count': workshop_paid_count,
        'speaking_session_form': form,
        'ss_success_msg': success_msg,
        'ss_error_msg': error_msg,
    })

def products_view(request):
    """Serve the products.html page."""
    workshop_paid_count = Payment.objects.filter(
        course_name='Cancer Nutrition Workshop',
        status='completed'
    ).count()
    workshop_sold_out = workshop_paid_count >= 20
    return render(request, 'products.html', {
        'workshop_sold_out': workshop_sold_out,
        'workshop_paid_count': workshop_paid_count,
    })

