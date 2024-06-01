from django.db import models
from django.contrib.auth.models import User
from crum import get_current_user


class purchase_order(models.Model):
    nomor_invoice = models.CharField(max_length=16)
    penjual = models.CharField(max_length=16)
    ekspedisi = models.CharField(max_length=16, null=True)
    tanggal = models.DateField()
    jatuh_tempo = models.DateField()
    status_pembayaran = models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    keterangan = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        try:
            name_str = f"{self.penjual}/{self.ekspedisi}/{self.tanggal.strftime('%d %b')}"
        except:
            name_str = f"{self.penjual}/{self.ekspedisi}/{self.tanggal}"
        return name_str


class item_PO(models.Model):
    purchase_order = models.ForeignKey(purchase_order, on_delete=models.CASCADE, related_name="item_PO")
    item = models.ForeignKey('Inventory.item', on_delete=models.DO_NOTHING, related_name="item_dalam_PO")

    harga = models.PositiveIntegerField()
    jumlah = models.PositiveIntegerField()
    keterangan = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.purchase_order}\t{self.item} QTY: {self.jumlah:,}"


class pengiriman(models.Model):
    purchase_order = models.ForeignKey(purchase_order, on_delete=models.CASCADE, related_name="pengiriman_dalam_PO")
    admin = models.ForeignKey(User, default=get_current_user, on_delete=models.DO_NOTHING)

    tanggal = models.DateField()
    tanggal_sampai = models.DateField(null=True, blank=True)
    keterangan = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        myDict = {}
        for index, entry in enumerate(pengiriman.objects.filter(purchase_order=self.purchase_order)):
            myDict[entry] = index
        return f"{self.purchase_order}/{myDict[self] + 1:,}"


class item_pengiriman(models.Model):
    pengiriman = models.ForeignKey(pengiriman, on_delete=models.CASCADE, related_name="item_pengiriman")
    item_PO = models.ForeignKey(item_PO, on_delete=models.CASCADE, related_name="item_dalam_pengiriman")

    ongkos = models.PositiveIntegerField()
    jumlah = models.PositiveIntegerField()
    keterangan = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.pengiriman} | {self.item_PO.item} ({self.jumlah:,})"
