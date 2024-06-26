# Generated by Django 4.2.7 on 2023-11-08 15:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Inventory', '0002_masuk_gudang_keluar_gudang_item_masuk_item_keluar'),
        ('Purchasing', '0002_rename_invoice_purchase_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item_invoice',
            name='invoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_PO', to='Purchasing.purchase_order'),
        ),
        migrations.AlterField(
            model_name='item_invoice',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='item_dalam_PO', to='Inventory.item'),
        ),
        migrations.AlterField(
            model_name='pengiriman',
            name='invoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pengiriman_dalam_PO', to='Purchasing.purchase_order'),
        ),
    ]
