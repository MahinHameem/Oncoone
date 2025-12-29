from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_add_registration_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentOTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('otp_code', models.CharField(max_length=6)),
                ('is_verified', models.BooleanField(default=False)),
                ('attempts', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('payment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='otp', to='core.payment')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
