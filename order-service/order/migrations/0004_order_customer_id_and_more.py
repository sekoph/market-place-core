# Generated by Django 5.2.1 on 2025-05-30 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_remove_order_order_order_custome_df6711_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='customer_id',
            field=models.UUIDField(default=2),
            preserve_default=False,
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['customer_id'], name='order_order_custome_df6711_idx'),
        ),
    ]
