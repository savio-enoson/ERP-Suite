# Generated by Django 4.2.7 on 2023-11-16 21:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Purchasing', '0006_rename_item_item_pengiriman_item_po'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item_pengiriman',
            name='jumlah_terima',
        ),
    ]