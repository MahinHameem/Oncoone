"""
Seed script to create sample courses in the database
Run with: python seed_courses.py
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Course
from decimal import Decimal


def seed_courses():
    """Create sample courses"""
    
    courses_data = [
        {
            'course_name': 'Oncology Esthetics Certificate',
            'course_code': 'OEC01',
            'description': 'Comprehensive oncology esthetics certification program',
            'price_cad': Decimal('2500.00'),
            'duration_weeks': 12,
            'requires_prerequisite': True,
            'is_active': True,
        },
        {
            'course_name': 'Pre-Certificate Bridge Course',
            'course_code': 'BRIDGE01',
            'description': 'Bridge course for students without esthetics certification',
            'price_cad': Decimal('1500.00'),
            'duration_weeks': 8,
            'requires_prerequisite': False,
            'is_active': True,
        },
        {
            'course_name': 'Advanced Oncology Skincare',
            'course_code': 'AOS01',
            'description': 'Advanced techniques in oncology skincare',
            'price_cad': Decimal('1800.00'),
            'duration_weeks': 6,
            'requires_prerequisite': True,
            'is_active': True,
        },
        {
            'course_name': 'Oncology Makeup Techniques',
            'course_code': 'OMT01',
            'description': 'Specialized makeup application for oncology patients',
            'price_cad': Decimal('1200.00'),
            'duration_weeks': 4,
            'requires_prerequisite': True,
            'is_active': True,
        },
    ]
    
    created_count = 0
    updated_count = 0
    
    for course_data in courses_data:
        course, created = Course.objects.update_or_create(
            course_code=course_data['course_code'],
            defaults=course_data
        )
        
        if created:
            created_count += 1
            print(f"✓ Created: {course.course_name} ({course.course_code}) - CAD ${course.price_cad}")
        else:
            updated_count += 1
            print(f"↻ Updated: {course.course_name} ({course.course_code}) - CAD ${course.price_cad}")
    
    print(f"\n✓ Course seeding complete!")
    print(f"  Created: {created_count} courses")
    print(f"  Updated: {updated_count} courses")
    print(f"  Total: {Course.objects.count()} courses in database")


if __name__ == '__main__':
    print("=" * 60)
    print("Seeding Courses into Database")
    print("=" * 60)
    seed_courses()
