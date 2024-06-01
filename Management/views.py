from django.http import JsonResponse
from django.template.loader import render_to_string

from django.contrib.auth.decorators import login_required

from django.utils.timezone import localdate
import datetime
import json

from django.db.models import Sum, Min, Q

from Purchasing.models import purchase_order, pengiriman
from Sales.models import transaksi, item_transaksi
from Inventory.models import item, stack, item_masuk, item_keluar, gudang


@login_required
def index(request):
    timeframe = [localdate() - datetime.timedelta(7), localdate()]
    head = 20

    incomplete_tr = transaksi.objects.filter(Q(status_pembayaran=False) | Q(status=False)).order_by('-tanggal',
                                                                                                    '-waktu')
    incomplete_items = item.objects.filter(Q(modal=0) | Q(harga=0) | Q(ongkos=0))

    flagged_items = []

    recently_sold = item_transaksi.objects.filter(transaksi__tanggal__range=timeframe).values('item_id').distinct()[
                    :head]
    for row in recently_sold:
        record = item.objects.get(id=row['item_id'])
        flags = record.barang_terjual.filter(transaksi__tanggal__range=timeframe).exclude(harga=record.harga)
        if len(flags) >= 1:
            flagged_items.append(record)

    flagged_stock = []
    recent_out = item_keluar.objects.filter(parent__tanggal__range=timeframe) \
                     .values('gudang_id', 'item_parent_id').distinct()[:head]
    recent_in = item_masuk.objects.filter(parent__tanggal__range=timeframe) \
                    .values('gudang_id', 'item_parent_id').distinct()[:head]

    combined_pairs = list(recent_out) + list(recent_in)
    for row in combined_pairs:
        gudang_id = row['gudang_id']
        item_parent_id = row['item_parent_id']
        try:
            record = stack.objects.get(gudang_id=gudang_id, item_id=item_parent_id)
        except:
            record = {
                "item": item.objects.get(id=item_parent_id), "gudang": gudang.objects.get(id=gudang_id)
            }

        flagged_stock.append(record)

    incomplete_po = purchase_order.objects.filter(Q(status=False) | Q(status_pembayaran=False))
    incomplete_pg = pengiriman.objects.filter(tanggal_sampai=None)

    context = {
        "header": "Dashboard Admin",
        "incomplete_tr": incomplete_tr.exclude(status=True),
        "pending_payment_tr": incomplete_tr.exclude(status=False),
        "incomplete_items": incomplete_items,
        "flagged_items": flagged_items,
        "flagged_stock": flagged_stock,
        "incomplete_po": incomplete_po.exclude(status=True),
        "pending_payment_po": incomplete_po.exclude(status=False),
        "incomplete_pg": incomplete_pg
    }

    page_content = render_to_string('Management/index.html', context)

    return JsonResponse({
        'content': page_content,
        'title': 'Admin | Dashboard Admin',
        'heading': 'Admin'
    })
