# Generated by Django 4.2.7 on 2023-11-08 14:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='gudang',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama', models.CharField(max_length=16)),
                ('keterangan', models.CharField(blank=True, default='', max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama', models.CharField(max_length=32)),
                ('harga', models.PositiveIntegerField()),
                ('modal', models.PositiveIntegerField()),
                ('ongkos', models.PositiveIntegerField()),
                ('satuan', models.CharField(max_length=12)),
                ('archived', models.BooleanField(default=True)),
                ('keterangan', models.CharField(blank=True, default='', max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='stack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jumlah', models.PositiveIntegerField()),
                ('expired', models.DateField(blank=True, default=None, null=True)),
                ('keterangan', models.CharField(blank=True, default='', max_length=200, null=True)),
                ('gudang', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='barang_dalam_gudang', to='Inventory.gudang')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='barang_dalam_stack', to='Inventory.item')),
            ],
        ),
    ]
