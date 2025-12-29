import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import CoursePrice

# Add the two courses
courses = [
    {
        'course_name': 'Pre-Certificate Bridge Course',
        'price_cad': 400.00,
        'description': 'Pre-Certificate Bridge Course - Prepare for the Oncology Esthetics Certificate program'
    },
    {
        'course_name': 'Oncology Esthetics Certificate',
        'price_cad': 800.00,
        'description': 'Oncology Esthetics Certificate - Complete certification program in oncology esthetics'
    }
]

for course_data in courses:
    course, created = CoursePrice.objects.update_or_create(
        course_name=course_data['course_name'],
        defaults={
            'price_cad': course_data['price_cad'],
            'description': course_data['description']
        }
    )
    if created:
        print(f"✓ Created: {course.course_name} - CAD ${course.price_cad}")
    else:
        print(f"✓ Updated: {course.course_name} - CAD ${course.price_cad}")

# Display all courses
print("\n" + "="*80)
print("All Courses in Database:")
print("="*80)
for course in CoursePrice.objects.all():
    print(f"Course: {course.course_name}")
    print(f"Price: CAD ${course.price_cad}")
    print(f"Description: {course.description}")
    print("-"*80)
