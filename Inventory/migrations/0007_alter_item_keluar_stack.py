# Generated by Django 5.0 on 2024-01-06 01:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Inventory', '0006_alter_gudang_keterangan_alter_item_keterangan_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item_keluar',
            name='stack',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Inventory.stack'),
        ),
    ]
