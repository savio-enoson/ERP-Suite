from django.contrib import admin
from .models import *
from Inventory.models import *
from Purchasing.models import *
from Sales.models import *

# MANAGEMENT MODELS
admin.site.register(session)
admin.site.register(changelog)

# INVENTORY MODELS
admin.site.register(gudang)
admin.site.register(item)
admin.site.register(stack)
admin.site.register(keluar_gudang)
admin.site.register(item_keluar)
admin.site.register(masuk_gudang)
admin.site.register(item_masuk)

# PURCASHING MODELS
admin.site.register(purchase_order)
admin.site.register(item_PO)
admin.site.register(pengiriman)
admin.site.register(item_pengiriman)

# SALES MODELS
admin.site.register(transaksi)
admin.site.register(item_transaksi)
admin.site.register(print_request)