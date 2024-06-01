from django.db import models
from django.contrib.auth.models import User
from crum import get_current_user
from django.utils import timezone


class transaksi (models.Model):
    pelanggan = models.CharField(max_length=16)
    tanggal = models.DateField(default=timezone.localdate)
    waktu = models.TimeField(default=timezone.localtime)
    pembayaran = models.CharField(max_length=16)
    admin = models.ForeignKey(User, on_delete=models.DO_NOTHING, default=get_current_user,
                              related_name="admin_transaksi")
    keterangan = models.CharField(max_length=200, null=True, blank=True)

    status_pembayaran = models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    metode_pembayaran = models.CharField(max_length=8, null=True, default=None)
    tanggal_pembayaran = models.DateField(null=True, default=None)

    def __str__(self):
        try:
            name_str = f"{self.pelanggan}/{self.tanggal.strftime('%d %b')}"
        except:
            name_str = f"{self.pelanggan}/{self.tanggal}"

        return name_str


class item_transaksi (models.Model):
    transaksi = models.ForeignKey(transaksi, on_delete=models.CASCADE, related_name="item_dalam_transaksi")
    item = models.ForeignKey('Inventory.item', on_delete=models.DO_NOTHING, related_name="barang_terjual")
    jumlah = models.PositiveIntegerField()
    harga = models.PositiveIntegerField()
    keterangan = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.transaksi} | {self.item} @Rp{self.harga:,} x {self.jumlah:,}"


class print_request(models.Model):
    transaksi = models.ForeignKey(transaksi, on_delete=models.CASCADE)

    printer_key = models.CharField(max_length=15, null=False, blank=False)
    status = models.BooleanField(default=False)
    nominal_bayar = models.PositiveIntegerField(blank=True, null=True, default=0)
    date = models.DateField(default=timezone.localdate)
    time = models.TimeField(default=timezone.localtime)

    def __str__(self):
        return f"{self.transaksi} on {self.printer_key}, at {self.date} - {self.time}"