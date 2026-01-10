# Generated migration for enhanced OTP security features

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_remove_registration_auto_bridge_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='paymentotp',
            index=models.Index(fields=['payment', 'is_verified'], name='core_paymen_payment_idx'),
        ),
        migrations.AddIndex(
            model_name='paymentotp',
            index=models.Index(fields=['expires_at', 'is_verified'], name='core_paymen_expires_idx'),
        ),
        migrations.AddField(
            model_name='paymentotp',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='paymentotp',
            name='otp_code',
            field=models.CharField(db_index=True, max_length=6),
        ),
        migrations.AlterField(
            model_name='paymentotp',
            name='is_verified',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='paymentotp',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='paymentotp',
            name='expires_at',
            field=models.DateTimeField(db_index=True),
        ),
    ]
