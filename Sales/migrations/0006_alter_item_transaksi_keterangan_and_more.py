# Generated by Django 5.0 on 2024-01-01 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Sales', '0005_transaksi_metode_pembayaran_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item_transaksi',
            name='keterangan',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='transaksi',
            name='keterangan',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
