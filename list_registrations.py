import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Registration

# Get all registrations
registrations = Registration.objects.all().order_by('-created_at')

if not registrations:
    print("No registrations found")
else:
    print("\n" + "="*120)
    print(f"{'ID':<5} {'Registration ID':<20} {'Name':<20} {'Email':<30} {'Courses':<25} {'Created':<20}")
    print("="*120)
    
    for reg in registrations:
        # Get all enrolled courses
        enrollments = reg.course_enrollments.all()
        courses = ', '.join([e.course_name[:20] for e in enrollments]) if enrollments else 'None'
        print(f"{reg.id:<5} {reg.registration_id:<20} {reg.name:<20} {reg.email:<30} {courses:<25} {reg.created_at.strftime('%Y-%m-%d %H:%M'):<20}")
    
    print("="*120)
    print(f"Total: {registrations.count()} students\n")
