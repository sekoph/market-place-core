# Generated by Django 5.2.1 on 2025-05-30 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0002_remove_customer_keycloak_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='keycloak_user_id',
            field=models.UUIDField(default=2, unique=True),
            preserve_default=False,
        ),
    ]
