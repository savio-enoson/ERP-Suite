# Generated by Django 5.0 on 2024-01-01 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Purchasing', '0009_alter_purchase_order_ekspedisi'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item_pengiriman',
            name='keterangan',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='item_po',
            name='keterangan',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='pengiriman',
            name='keterangan',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='purchase_order',
            name='keterangan',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
