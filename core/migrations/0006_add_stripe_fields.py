from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_add_payment_otp'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='stripe_payment_intent_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='stripe_charge_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='stripe_customer_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
