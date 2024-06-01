from django.db import models
from django.contrib.auth.models import User
from crum import get_current_user
from django.utils import timezone

class gudang (models.Model):
    nama = models.CharField(max_length=16)
    keterangan = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.nama


class item (models.Model):
    nama = models.CharField(max_length=32)
    harga = models.PositiveIntegerField()
    modal = models.PositiveIntegerField()
    ongkos = models.PositiveIntegerField()
    satuan = models.CharField(max_length=12)
    archived = models.BooleanField(default=True)
    keterangan = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.nama} ({self.satuan})"


class stack (models.Model):
    item = models.ForeignKey(item, on_delete=models.CASCADE, related_name="barang_dalam_stack")
    gudang = models.ForeignKey(gudang, on_delete=models.CASCADE, related_name="barang_dalam_gudang")

    jumlah = models.PositiveIntegerField(default=0)
    expired = models.DateField(default=None, null=True, blank=True)
    keterangan = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.item.nama} - {self.gudang} QTY: {self.jumlah:,}"


class keluar_gudang (models.Model):
    transaksi = models.ForeignKey('Sales.transaksi', on_delete=models.CASCADE, related_name="record_keluar"
                                  , null=True, blank=True)
    admin = models.ForeignKey(User, on_delete=models.DO_NOTHING, default=get_current_user)

    tanggal = models.DateField(default=timezone.localdate)
    waktu = models.TimeField(default=timezone.localtime)

    def __str__(self):
        myDict = {}
        for index, entry in enumerate(keluar_gudang.objects.filter(transaksi=self.transaksi)):
            myDict[entry] = index
        return f"{self.transaksi}/{myDict[self] + 1:,}"


class item_keluar (models.Model):
    parent = models.ForeignKey(keluar_gudang, on_delete=models.CASCADE, related_name="item_dalam_record_keluar")
    gudang = models.ForeignKey(gudang, on_delete=models.DO_NOTHING, null=True)
    stack = models.ForeignKey(stack, on_delete=models.SET_NULL, null=True, blank=True)
    item = models.ForeignKey('Sales.item_transaksi', on_delete=models.DO_NOTHING, null=True)
    item_parent = models.ForeignKey('Inventory.item', on_delete=models.CASCADE, related_name="item_keluar")

    jumlah = models.PositiveIntegerField()
    jumlah_awal = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.parent}/{self.item} - {self.gudang} QTY: {self.jumlah_awal:,} -> {self.jumlah_awal - self.jumlah:,}"


class masuk_gudang (models.Model):
    pengiriman = models.ForeignKey('Purchasing.pengiriman', on_delete=models.CASCADE, related_name="record_masuk"
                                   , null=True, blank=True)
    admin = models.ForeignKey(User, on_delete=models.DO_NOTHING, default=get_current_user)

    tanggal = models.DateField(default=timezone.localdate)
    waktu = models.TimeField(default=timezone.localtime)

    def __str__(self):
        myDict = {}
        for index, entry in enumerate(masuk_gudang.objects.filter(pengiriman=self.pengiriman)):
            myDict[entry] = index
        return f"{self.pengiriman}/{myDict[self] + 1:,}"


class item_masuk (models.Model):
    parent = models.ForeignKey(masuk_gudang, on_delete=models.CASCADE, related_name="item_dalam_record_masuk")
    gudang = models.ForeignKey(gudang, on_delete=models.SET_NULL, null=True)
    item = models.ForeignKey('Purchasing.item_pengiriman', on_delete=models.DO_NOTHING, null=True, related_name='item_diterima')
    item_parent = models.ForeignKey('Inventory.item', on_delete=models.CASCADE, related_name="item_masuk")

    jumlah = models.PositiveIntegerField()
    jumlah_awal = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.parent}/{self.item} - {self.gudang} QTY: {self.jumlah_awal:,} -> {self.jumlah_awal + self.jumlah:,}"


