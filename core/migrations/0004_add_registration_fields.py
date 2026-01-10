from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_5_cleanup_duplicate_emails'),
    ]

    operations = [
        # Make email unique to prevent duplicate registrations
        migrations.AlterField(
            model_name='registration',
            name='email',
            field=models.EmailField(db_index=True, max_length=254, unique=True),
        ),
        # Add updated_at field for tracking changes
        migrations.AddField(
            model_name='registration',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]



