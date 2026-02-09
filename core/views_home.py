from django.shortcuts import render
from django.db.models import Count

from .models import Payment

def index_view(request):
    """Serve the index.html homepage."""
    workshop_paid_count = Payment.objects.filter(
        course_name='Cancer Nutrition Workshop',
        status='completed'
    ).count()
    workshop_sold_out = workshop_paid_count >= 20
    return render(request, 'index.html', {
        'workshop_sold_out': workshop_sold_out,
        'workshop_paid_count': workshop_paid_count,
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

