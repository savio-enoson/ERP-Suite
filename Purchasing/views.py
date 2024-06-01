from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required

from django.utils.formats import date_format, number_format
from django.utils.timezone import localdate
import datetime
import json

from django.db.models import Sum, Min, Q, F
from django.db.models.functions import Coalesce

from .models import purchase_order, pengiriman, item_PO, item_pengiriman
from Inventory.models import item_masuk, gudang, masuk_gudang, stack


def map_status(status, payment):
    # Sudah selesai sudah bayar
    if status and payment:
        return {"color": "green", "text": "Selesai", "selesai": True, "lunas": True}
    # Sudah bayar, belum selesai
    if not status and payment:
        return {"color": "blue", "text": "Menunggu", "selesai": False, "lunas": True}
    if status and not payment:
        return {"color": "yellow", "text": "Hutang", "selesai": True, "lunas": False}
    if not status and not payment:
        return {"color": "gray", "text": "Draft", "selesai": False, "lunas": False}


@login_required
def riwayat_purchase_order(request):
    query = purchase_order.objects.all().order_by('-tanggal')[:200]
    status = []
    total_harga = []

    for row in query:
        my_total = row.item_PO.all().aggregate(total=Sum(F('jumlah') * F('harga')))['total']
        my_total = int(0 if my_total is None else my_total)
        total_harga.append(my_total)

        status.append(map_status(row.status, row.status_pembayaran))

    context = {
        "header": "Riwayat PO / Invoice",
        "riwayat": zip(query, status, total_harga)
    }

    page_content = render_to_string('Purchasing/index.html', context)

    return JsonResponse({
        'content': page_content,
        'title': 'Pembelian | Riwayat PO',
        'heading': 'Pembelian'
    })


@login_required
def get_po(request):
    my_id = request.GET.get('id')

    my_record = purchase_order.objects.get(id=my_id)
    my_items = my_record.item_PO.all().annotate(diterima=Coalesce(Sum('item_dalam_pengiriman__item_diterima__jumlah'), 0))

    context = {
        "purchase_order": {
            "id": my_id,
            "nomor": my_record.nomor_invoice,
            "header": f"{my_record.penjual} | {date_format(my_record.tanggal)} | {my_record.ekspedisi}",
            "status": map_status(my_record.status, my_record.status_pembayaran),
            "keterangan": "" if my_record.keterangan is None else my_record.keterangan
        },
        "item_po": my_items,
        "grand_total": my_items.aggregate(total=Sum(F('diterima') * F('harga')))['total'],
        "ada_keterangan": my_items.exclude(keterangan__exact='').exclude(keterangan__isnull=True).exists()
    }

    modal_content = render_to_string('Purchasing/get_po.html', context)
    return JsonResponse({'content': modal_content})


@login_required
def get_barang_masuk(request):
    my_id = request.GET.get('id')
    type = request.GET.get('type')

    # Buffer values
    my_po = None
    my_object = None
    list_pengiriman = []

    # Get all pengiriman from purchase order
    if type == '0':
        my_po = purchase_order.objects.get(id=my_id)

        for row in my_po.pengiriman_dalam_PO.all():
            list_masuk = []
            for i in row.record_masuk.all():
                for j in i.item_dalam_record_masuk.all():
                    list_masuk.append({
                        "nama": str(j.item_parent),
                        "gudang": j.gudang.nama,
                        "jumlah": j.item.jumlah,
                        "diterima": j.jumlah
                    })

            list_pengiriman.append({
                "record": row,
                "items": list_masuk
            })
    # Get pengiriman with item_masuk id
    elif type == '1':
        list_masuk = []
        my_object = item_masuk.objects.get(id=my_id)
        my_pengiriman = my_object.parent.pengiriman
        my_po = my_pengiriman.purchase_order

        for i in my_pengiriman.record_masuk.all():
            for j in i.item_dalam_record_masuk.all():
                list_masuk.append({
                    "nama": str(j.item_parent),
                    "gudang": j.gudang.nama,
                    "jumlah": j.item.jumlah,
                    "diterima": j.jumlah
                })

        list_pengiriman.append({
            "record": my_pengiriman,
            "items": list_masuk
        })
    # Get pengiriman with pengiriman id
    elif type == '2':
        list_masuk = []
        my_pengiriman = pengiriman.objects.get(id=my_id)
        my_po = my_pengiriman.purchase_order

        for i in my_pengiriman.record_masuk.all():
            for j in i.item_dalam_record_masuk.all():
                list_masuk.append({
                    "nama": str(j.item_parent),
                    "gudang": j.gudang.nama,
                    "jumlah": j.item.jumlah,
                    "diterima": j.jumlah
                })

        list_pengiriman.append({
            "record": my_pengiriman,
            "items": list_masuk
        })

    context = {
        "id": my_po.id,
        "type": type,
        "header": f"{my_po.penjual} | {my_po.ekspedisi} | {my_po.tanggal}",
        "list_pengiriman": list_pengiriman
    }

    modal_content = render_to_string('Purchasing/get_barang_masuk.html', context)
    return JsonResponse({'content': modal_content})


@login_required
def get_pengiriman(request):
    my_id = request.GET.get('id')

    my_po = purchase_order.objects.get(id=my_id)
    grand_total = 0
    list_pengiriman = []

    for row in my_po.pengiriman_dalam_PO.all():
        list_item_pengiriman = row.item_pengiriman.all().annotate(diterima=Coalesce(Sum('item_diterima__jumlah'), 0))
        my_total = list_item_pengiriman.aggregate(total=Sum(F('ongkos') * F('diterima')))['total']
        grand_total += my_total
        list_pengiriman.append({
            "record": row,
            "sampai": row.tanggal_sampai is not None,
            "items": list_item_pengiriman,
            "total_ongkos": my_total,
            "ada_keterangan": row.item_pengiriman.all().exclude(keterangan__exact='').exclude(
                keterangan__isnull=True).exists(),
        })

    context = {
        "id": my_po.id,
        "header": f"{my_po.penjual} | {my_po.ekspedisi} | {my_po.tanggal}",
        "list_pengiriman": list_pengiriman,
        "grand_total": grand_total
    }

    modal_content = render_to_string('Purchasing/get_pengiriman.html', context)
    return JsonResponse({'content': modal_content})


@login_required
def modify_po(request):
    my_id = request.GET.get('id')

    my_record = purchase_order.objects.get(id=my_id) if my_id else {
        "id": None, "penjual": "", "ekspedisi": "", "nomor_invoice": "",
        "tanggal": localdate(), "jatuh_tempo": localdate() + datetime.timedelta(days=30),
        "status_pembayaran": False, "status": False, "keterangan": ""
    }

    record_items = []
    if my_id != '':
        for row in my_record.item_PO.all():
            record_items.append({
                "id": row.item.id,
                "nama": row.item.nama,
                "label": str(row.item),
                "jumlah": row.jumlah,
                "harga": row.harga,
                "harga_total": row.jumlah * row.harga,
                "keterangan": "" if row.keterangan is None else row.keterangan
            })

    modal_content = render_to_string('Purchasing/modify_po.html', {
        "purchase_order": my_record,
        "item_po": json.dumps(record_items) if my_id != '' else None,
        "list_ekspedisi": purchase_order.objects.values('ekspedisi').distinct(),
        "list_penjual": purchase_order.objects.values('penjual').distinct()
    })
    return JsonResponse({'content': modal_content})


@login_required
def post_po(request):
    id_po = request.POST.get('id_po')
    penjual = request.POST.get('penjual').title()
    ekspedisi = request.POST.get('ekspedisi')
    nomor_invoice = request.POST.get('nomor_invoice')
    tanggal = request.POST.get('tanggal')
    jatuh_tempo = request.POST.get('jatuh_tempo')

    keterangan = request.POST.get('keterangan')
    keterangan = None if keterangan == "" else keterangan

    item_dalam_po = json.loads(request.POST.get('item_po'))
    target_item = None

    if id_po != "None":
        target_item = purchase_order.objects.get(id=id_po)
        updating = True
    else:
        updating = False

    if updating:
        target_item.penjual = penjual
        target_item.nomor_invoice = nomor_invoice
        target_item.ekspedisi = ekspedisi
        target_item.tanggal = tanggal
        target_item.jatuh_tempo = jatuh_tempo
        target_item.keterangan = keterangan
        target_item.save()
    else:
        target_item = purchase_order(penjual=penjual, nomor_invoice=nomor_invoice, ekspedisi=ekspedisi,
                                     tanggal=tanggal, jatuh_tempo=jatuh_tempo, keterangan=keterangan)
        target_item.save()

    if updating:
        target_item.item_PO.all().delete()

    for item in item_dalam_po:
        new_item = item_PO(purchase_order=target_item, item_id=item['id'], jumlah=item['jumlah'], harga=item['harga'],
                           keterangan=None if item['keterangan'] == "" else item['keterangan'])
        new_item.save()
        
    return JsonResponse({
        'message': f"Berhasil mengubah {target_item}" if updating else f"Berhasil menambahkan {target_item}"
    })


@login_required
def modify_pengiriman(request):
    my_id = request.GET.get('id')
    type = request.GET.get('type')

    my_record = None
    query = None
    ada_keterangan = False
    id_po = None

    # Type 0 = purchase order id (create new)
    if type == '0':
        my_record = {"id": None, "tanggal": localdate()}
        query = purchase_order.objects.get(id=my_id).item_PO.all()
        ada_keterangan = query.exclude(keterangan__exact='').exclude(keterangan__isnull=True).exists()
        id_po = my_id
    # Type 1 = pengiriman id (modify)
    elif type == '1':
        my_record = pengiriman.objects.get(id=my_id)
        query = my_record.purchase_order.item_PO.all()
        ada_keterangan = query.exclude(keterangan__exact='').exclude(keterangan__isnull=True).exists()
        id_po = my_record.purchase_order_id

    list_item_po = []
    for row in query:
        diterima = row.item_dalam_pengiriman.all().annotate(diterima=Sum('item_diterima__jumlah'))
        diterima = diterima.aggregate(total_terima=Sum('diterima'))['total_terima']
        list_item_po.append({
            "id": row.item.id,
            "id_item_po": row.id,
            "nama": row.item.nama,
            "satuan": row.item.satuan,
            "ongkos": row.item.ongkos,
            "label": str(row.item),
            "jumlah": row.jumlah,
            "diterima": diterima,
            "keterangan": row.keterangan
        })

    record_items = []
    if type == '1':
        for row in my_record.item_pengiriman.all():
            parent_item = row.item_PO.item
            record_items.append({
                "id": parent_item.id,
                "id_item_po": row.item_PO_id,
                "nama": parent_item.nama,
                "label": str(parent_item),
                "jumlah": row.jumlah,
                "harga": row.ongkos,
                "harga_total": row.jumlah * row.ongkos,
                "keterangan": "" if row.keterangan is None else row.keterangan
            })

    modal_content = render_to_string('Purchasing/modify_pengiriman.html', {
        "id_po": id_po,
        "pengiriman": my_record,
        "ada_keterangan": ada_keterangan,
        "item_po": list_item_po,
        "list_item_po": json.dumps(list_item_po),
        "item_pengiriman": json.dumps(record_items) if my_id != '' else None
    })
    return JsonResponse({'content': modal_content})


@login_required
def post_pengiriman(request):
    id_po = request.POST.get('id_po')
    id_pengiriman = request.POST.get('id_pengiriman')

    tanggal = request.POST.get('tanggal')
    keterangan = request.POST.get('keterangan')
    keterangan = None if keterangan == "" else keterangan

    item_dalam_pengiriman = json.loads(request.POST.get('item_pengiriman'))
    target_item = None

    if id_pengiriman != "None":
        target_item = pengiriman.objects.get(id=id_pengiriman)
        updating = True
    else:
        updating = False

    if updating:
        target_item = pengiriman.objects.get(id=id_pengiriman)
        target_item.tanggal = tanggal
        target_item.keterangan = keterangan
        target_item.save()
    else:
        target_item = pengiriman(purchase_order_id=id_po, tanggal=tanggal, keterangan=keterangan)
        target_item.save()

    if updating:
        target_item.item_pengiriman.all().delete()

    for item in item_dalam_pengiriman:
        new_item = item_pengiriman(pengiriman=target_item, item_PO_id=item['id_item_po'],
                                   jumlah=item['jumlah'], ongkos=item['harga'],
                                   keterangan=None if item['keterangan'] == "" else item['keterangan'])
        new_item.save()

    return JsonResponse({
        'message': f"Berhasil mengubah {target_item}" if updating else f"Berhasil menambahkan {target_item}"
    })


@login_required
def terima_pengiriman(request):
    my_id = request.GET.get('id')

    my_record = pengiriman.objects.get(id=my_id)

    modal_content = render_to_string('Purchasing/terima_pengiriman.html', {
        "pengiriman": my_record,
        "list_gudang": gudang.objects.all(),
        "item_pengiriman": my_record.item_pengiriman.all()
    })
    return JsonResponse({'content': modal_content})


@login_required
def post_barang_masuk(request):
    id_pengiriman = request.POST.get('id_pengiriman')
    tanggal_sampai = request.POST.get('tanggal_sampai')
    waktu = request.POST.get('jam_sampai')

    list_item_masuk = json.loads(request.POST.get('item_masuk'))
    target_item = masuk_gudang(pengiriman_id=id_pengiriman, tanggal=tanggal_sampai, waktu=waktu)
    target_item.save()

    for item in list_item_masuk:
        try:
            target_stack = stack.objects.get(item_id=item['item_parent_id'], gudang_id=item['gudang_id'])
        except:
            target_stack = stack(item_id=item['item_parent_id'], gudang_id=item['gudang_id'])

        new_item = item_masuk(parent=target_item, item_parent_id=item['item_parent_id'],
                              item_id=item['item_id'], gudang_id=item['gudang_id'],
                              jumlah=item['jumlah_terima'], jumlah_awal=target_stack.jumlah)
        new_item.save()

        target_stack.expired = None if item['expired'] == "" else item['expired']
        target_stack.keterangan = None if item['keterangan'] == "" else item['keterangan']
        target_stack.jumlah += item['jumlah_terima']
        target_stack.save()

    my_pengiriman = pengiriman.objects.get(id=id_pengiriman)
    my_pengiriman.tanggal_sampai = tanggal_sampai
    my_pengiriman.save()

    return JsonResponse({
        'message': f"Berhasil menambahkan {target_item}"
    })


@login_required
def riwayat_barang_masuk(request):
    context = {
        "header": "Riwayat Barang Masuk",
        "riwayat": masuk_gudang.objects.all().order_by('-tanggal', '-waktu')[:200]
    }

    page_content = render_to_string('Purchasing/riwayat_barang_masuk.html', context)

    return JsonResponse({
        'content': page_content,
        'title': 'Pembelian | Riwayat Barang Masuk',
        'heading': 'Pembelian'
    })


@login_required
def riwayat_pengiriman(request):
    context = {
        "header": "Riwayat Pengiriman",
        "list_pengiriman": pengiriman.objects.all()[:200]
    }

    page_content = render_to_string('Purchasing/riwayat_pengiriman.html', context)

    return JsonResponse({
        'content': page_content,
        'title': 'Pembelian | Riwayat Pengiriman',
        'heading': 'Pembelian'
    })