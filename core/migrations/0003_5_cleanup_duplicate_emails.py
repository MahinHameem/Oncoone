from django.db import migrations


def cleanup_duplicate_emails(apps, schema_editor):
    """Remove duplicate email records, keeping only the first occurrence"""
    Registration = apps.get_model('core', 'Registration')
    
    # Get all emails and their counts
    email_counts = {}
    duplicates_to_delete = []
    
    for reg in Registration.objects.all().order_by('id'):
        email = reg.email.lower() if reg.email else ''
        
        if email in email_counts:
            # This is a duplicate, mark for deletion
            duplicates_to_delete.append(reg.id)
        else:
            # First occurrence, keep it
            email_counts[email] = reg.id
    
    # Delete duplicate registrations
    if duplicates_to_delete:
        Registration.objects.filter(id__in=duplicates_to_delete).delete()
        print(f"Deleted {len(duplicates_to_delete)} duplicate registration(s)")


def reverse_cleanup(apps, schema_editor):
    """Reverse operation - nothing to do as we can't restore deleted data"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_courseprice_payment_paymentinvoice'),
    ]

    operations = [
        migrations.RunPython(cleanup_duplicate_emails, reverse_cleanup),
    ]
