# Generated by Django 4.2.7 on 2023-11-13 19:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Purchasing', '0005_rename_invoice_item_po_purchase_order_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item_pengiriman',
            old_name='item',
            new_name='item_PO',
        ),
    ]
