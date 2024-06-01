from Sales.views import map_status
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from django.utils.formats import date_format, number_format
from django.utils.timezone import localdate
import datetime

from django.db.models import Sum, Min, Q, F
from django.db.models.functions import Coalesce

from .models import item, stack, gudang, item_keluar, item_masuk, masuk_gudang, keluar_gudang
from Sales.models import transaksi, item_transaksi
from Purchasing.models import purchase_order
from Management.models import session


@login_required
def get_inventory(request):
    query = item.objects.filter(archived=False).order_by("nama")
    jumlah_item = []
    volume_jual = []
    expired = []
    inbound = []

    for i in query:
        my_total = i.barang_dalam_stack.all().aggregate(Sum('jumlah'))['jumlah__sum']
        my_total = int(0 if my_total is None else my_total)
        jumlah_item.append(my_total)

        volume = i.barang_terjual.filter(
            transaksi__tanggal__gt=localdate() - datetime.timedelta(days=60)).aggregate(Sum('jumlah'))[
            'jumlah__sum']
        volume = int(0 if volume is None else volume)
        volume_jual.append(volume)

        my_exp = i.barang_dalam_stack.all().aggregate(Min('expired'))['expired__min']
        my_exp = "-" if my_exp is None else my_exp
        expired.append(my_exp)

        inb_query = i.item_dalam_PO.filter(purchase_order__status=False)
        total_inbound = 0
        for j in inb_query:
            my_inbound = j.item_dalam_pengiriman.all().annotate(diterima=Coalesce(Sum('item_diterima__jumlah'), 0))
            my_inbound = my_inbound.aggregate(total=Sum(F('jumlah') - F('diterima')))['total']
            my_inbound = int(0 if my_inbound is None else my_inbound)
            total_inbound += my_inbound
        inbound.append(total_inbound)

    context = {
        "header": "Daftar Barang",
        "inventory": zip(query, jumlah_item, volume_jual, expired, inbound)
    }

    page_content = render_to_string('Inventory/index.html', context)

    return JsonResponse({
        'content': page_content,
        'title': 'Inventory Toko | Daftar Barang',
        'heading': 'Inventory'
    })


@login_required
def stock_gudang(request):
    # Get list stock
    query = stack.objects.all()
    list_stock = []
    for row in query:
        list_stock.append({
            "id": row.id,
            "nama": str(row.item),
            "gudang": row.gudang.nama,
            "satuan": row.item.satuan,
            "jumlah": row.jumlah,
            "expired": "-" if not row.expired else date_format(row.expired, "j N Y"),
            "keterangan": "" if not row.keterangan else row.keterangan
        })

    # Get list activiy
    list_activity = []
    num_days = 30
    timeframe = [localdate() - datetime.timedelta(num_days), localdate()]

    for row in item_masuk.objects.filter(parent__tanggal__range=timeframe):
        jumlah_akhir = row.jumlah_awal + row.jumlah
        record = {
            "id": row.id,
            "barang": str(row.item_parent),
            "ref": row.parent.pengiriman.purchase_order.ekspedisi,
            "gudang": row.gudang.nama,
            "tanggal": row.parent.tanggal,
            "waktu": row.parent.waktu,
            "jumlah": row.jumlah,
            "jumlah_awal": row.jumlah_awal,
            "jumlah_akhir": jumlah_akhir,
            "selisih": jumlah_akhir - row.jumlah_awal,
            "type": 1
        }
        list_activity.append(record)

    for row in item_keluar.objects.filter(parent__tanggal__range=timeframe):
        jumlah_akhir = row.jumlah_awal - row.jumlah
        record = {
            "id": row.id,
            "barang": str(row.item_parent),
            "ref": row.parent.transaksi.pelanggan,
            "gudang": row.gudang.nama,
            "tanggal": row.parent.tanggal,
            "waktu": row.parent.waktu,
            "jumlah": row.jumlah,
            "jumlah_awal": row.jumlah_awal,
            "jumlah_akhir": jumlah_akhir,
            "selisih": row.jumlah_awal - jumlah_akhir,
            "type": 0
        }
        list_activity.append(record)

    list_activity = sorted(list_activity, key=lambda d: (d['tanggal'], d['waktu']), reverse=True)

    # Compile page
    list_gudang = gudang.objects.all()
    context = {
        "header": "Stock Gudang",
        "list_gudang": list_gudang,
        'list_stock': list_stock,
        "list_activity": list_activity
    }

    page_content = render_to_string('Inventory/stock_gudang.html', context)

    return JsonResponse({
        'content': page_content,
        'title': 'Inventory Toko | Stock Gudang',
        'heading': 'Inventory',
    })


@login_required
def modify_item(request):
    my_id = request.GET.get('id')

    my_record = item.objects.get(id=my_id) if my_id else {
        "id": None, "nama": "", "harga": 0, "modal": 0,
        "ongkos": 0, "satuan": "", "keterangan": "", "archived": False
    }

    modal_content = render_to_string('Inventory/modify_item.html', {
        "item": my_record
    })
    return JsonResponse({'content': modal_content})


@login_required
def post_item(request):
    id_item = request.POST.get('id_item')
    nama = request.POST.get('nama')
    satuan = request.POST.get('satuan').title()
    harga = request.POST.get('harga')
    modal = request.POST.get('modal')
    ongkos = request.POST.get('ongkos')
    archived = request.POST.get('archived')
    keterangan = request.POST.get('keterangan')
    keterangan = None if keterangan == "" else keterangan

    if id_item != "None":
        updating = item.objects.get(id=id_item)
        updating = True
    else:
        updating = False

    if updating:
        target_item = item.objects.get(id=id_item)
        target_item.nama = nama
        target_item.harga = harga
        target_item.modal = modal
        target_item.ongkos = ongkos
        target_item.satuan = satuan
        target_item.archived = archived
        target_item.keterangan = keterangan
        target_item.save()
    else:
        new_item = item(nama=nama, satuan=satuan, harga=harga, modal=modal,
                        ongkos=ongkos, archived=archived, keterangan=keterangan)
        new_item.save()

    return JsonResponse({
        'message': f"Berhasil mengubah {nama}" if updating else f"Berhasil menambahkan {nama}"
    })


@login_required
def get_stack(request):
    my_id = request.GET.get('id')
    my_item = item.objects.get(id=my_id)

    stacks = my_item.barang_dalam_stack.all()

    item_activity = []

    for row in my_item.item_masuk.filter(parent__tanggal__range=
                                         [localdate() - datetime.timedelta(30), localdate()]):
        jumlah_akhir = row.jumlah_awal + row.jumlah
        record = {
            "id": row.id,
            "ref": row.parent.pengiriman.purchase_order.ekspedisi,
            "gudang": row.gudang,
            "tanggal": row.parent.tanggal,
            "waktu": row.parent.waktu,
            "jumlah": row.jumlah,
            "jumlah_awal": row.jumlah_awal,
            "jumlah_akhir": jumlah_akhir,
            "selisih": jumlah_akhir - row.jumlah_awal,
            "type": 1
        }
        item_activity.append(record)

    for row in my_item.item_keluar.filter(parent__tanggal__range=
                                          [localdate() - datetime.timedelta(30), localdate()]):
        jumlah_akhir = row.jumlah_awal - row.jumlah
        record = {
            "id": row.id,
            "ref": row.parent.transaksi.pelanggan,
            "gudang": row.gudang,
            "tanggal": row.parent.tanggal,
            "waktu": row.parent.waktu,
            "jumlah": row.jumlah,
            "jumlah_awal": row.jumlah_awal,
            "jumlah_akhir": jumlah_akhir,
            "selisih": row.jumlah_awal - jumlah_akhir,
            "type": 0
        }
        item_activity.append(record)

    item_activity = sorted(item_activity, key=lambda d: (d['tanggal'], d['waktu']), reverse=True)

    modal_content = render_to_string('Inventory/get_stack.html', {
        "item": my_item,
        "stacks": stacks,
        "item_activity": item_activity
    })
    return JsonResponse({'content': modal_content})


@login_required
def get_item_list(request):
    item_list = []
    for row in item.objects.filter(archived=False):
        item_list.append({
            "id": row.id, "nama": row.nama, "satuan": row.satuan,
            "harga": row.harga, "modal": row.modal, "label": str(row),
        })

    return JsonResponse({'item_list': item_list})


@login_required
def modify_stack(request):
    my_id = request.GET.get('id')

    my_record = stack.objects.get(id=my_id)

    modal_content = render_to_string('Inventory/modify_stack.html', {
        "stack": my_record
    })
    return JsonResponse({'content': modal_content})


@login_required
def post_stack(request):
    id_stack = request.POST.get('id_stack')
    expired = request.POST.get('expired')
    expired = None if expired == "" else expired
    jumlah = request.POST.get('jumlah')
    keterangan = request.POST.get('keterangan')
    keterangan = None if keterangan == "" else keterangan

    target_item = stack.objects.get(id=id_stack)
    target_item.expired = expired
    target_item.jumlah = jumlah
    target_item.keterangan = keterangan
    target_item.save()

    return JsonResponse({
        'message': f"Berhasil mengubah {target_item.item} - {target_item.gudang}."
    })


@login_required
def get_item_stock(request):
    my_id = request.GET.get('id')
    my_item = item.objects.get(id=my_id)
    stock = my_item.barang_dalam_stack.all().aggregate(total=Sum('jumlah'))['total']
    stock = 0 if stock == None else stock

    return JsonResponse({
        'stock': f"{number_format(stock, use_l10n=True)} {my_item.satuan}"
    })


@login_required
def lunaskan(request):
    my_id = request.POST.get('id')
    type = request.POST.get('type')

    if type == '0':
        param = request.POST.get('param')
        record = transaksi.objects.get(id=my_id)
        record.status_pembayaran = True
        record.metode_pembayaran = param
        record.tanggal_pembayaran = timezone.localtime()
        record.save()
    elif type == '1':
        record = purchase_order.objects.get(id=my_id)
        record.status_pembayaran = True
        record.save()

    return JsonResponse({
        'status': 1
    })


@login_required
def selesaikan(request):
    my_id = request.POST.get('id')
    type = request.POST.get('type')

    if type == '0':
        record = transaksi.objects.get(id=my_id)
        record.status = True
        record.save()
    elif type == '1':
        record = purchase_order.objects.get(id=my_id)
        record.status = True
        record.save()

    return JsonResponse({'status': 1})


@login_required
def kembali_ke_draft(request):
    my_id = request.POST.get('id')
    type = request.POST.get('type')

    # TRANSAKSI
    if type == '0':
        record = transaksi.objects.get(id=my_id)
        record.status = False
        record.status_pembayaran = False
        record.metode_pembayaran = None
        record.tanggal_pembayaran = None
        record.save()
    # PURCHASE ORDER
    elif type == '1':
        record = purchase_order.objects.get(id=my_id)
        record.status = False
        record.status_pembayaran = False
        record.save()

    return JsonResponse({'status': 1})


@login_required
def create_recap(request):
    page_content = render_to_string('Inventory/create_recap.html')

    return JsonResponse({
        'content': page_content,
        'title': 'Inventory | Buat Rekapan',
        'heading': 'Inventory'
    })


@login_required
def get_recap(request):
    mulai = request.GET.get('mulai')

    sampai = request.GET.get('sampai')
    timeframe = f"{mulai} - {sampai}" if sampai != "" else mulai
    sampai = mulai if sampai is "" else sampai

    query_transaksi = transaksi.objects.filter(tanggal__range=[mulai, sampai]).order_by('-tanggal', '-waktu')
    list_item_transaksi = []
    status = []
    total_harga = []
    total_value_tr = 0

    # RECAP TRANSAKSI
    for row in query_transaksi:
        my_total = row.item_dalam_transaksi.all().aggregate(total=Sum(F('jumlah') * F('harga')))['total']
        my_total = int(0 if my_total is None else my_total)
        total_harga.append(my_total)
        total_value_tr += my_total

        status.append(map_status(row.status, row.status_pembayaran))
        list_item_transaksi.append(row.item_dalam_transaksi.all())

    item_terjual = {}
    for i in list_item_transaksi:
        for j in i:
            try:
                item_terjual[j.item_id]['jumlah'] += j.jumlah
            except:
                item_terjual[j.item_id] = {'nama': str(j.item), 'jumlah': j.jumlah}


    # RECAP BARANG MASUK
    query_masuk = masuk_gudang.objects.filter(tanggal__range=[mulai, sampai]).order_by('-tanggal', '-waktu')
    list_item_masuk = []

    for row in query_masuk:
        list_item_masuk.append(row.item_dalam_record_masuk.all())

    sum_item_masuk = {}
    for i in list_item_masuk:
        for j in i:
            try:
                sum_item_masuk[f"{j.item_parent_id},{j.gudang_id}"]['jumlah'] \
                    += j.jumlah
            except:
                sum_item_masuk[f"{j.item_parent_id},{j.gudang_id}"] \
                    = {'nama': str(j.item_parent), 'gudang': str(j.gudang), 'jumlah': j.jumlah}


    # RECAP BARANG KELUAR
    query_keluar = keluar_gudang.objects.filter(tanggal__range=[mulai, sampai]).order_by('-tanggal', '-waktu')
    list_item_keluar = []

    for row in query_keluar:
        list_item_keluar.append(row.item_dalam_record_keluar.all())

    sum_item_keluar = {}
    for i in list_item_keluar:
        for j in i:
            try:
                sum_item_keluar[f"{j.item_parent_id},{j.gudang_id}"]['jumlah'] \
                    += j.jumlah
            except:
                sum_item_keluar[f"{j.item_parent_id},{j.gudang_id}"] \
                    = {'nama': str(j.item_parent), 'gudang': str(j.gudang), 'jumlah': j.jumlah}


    # STOCK BARANG
    flagged_items = []
    if mulai == timezone.localdate().strftime("%Y-%m-%d"):
        recent_items = item_transaksi.objects.order_by('-transaksi__tanggal').values_list('item', flat=True).distinct()[:20]
        for item_id in recent_items:
            record = item.objects.get(id=item_id)

            current_stock = record.barang_dalam_stack.all().aggregate(Sum('jumlah'))['jumlah__sum']
            current_stock = 0 if current_stock is None else current_stock
            monthly_demand = record.barang_terjual.filter(transaksi__tanggal__range=
                                  [timezone.localdate() - datetime.timedelta(days=30),
                                   timezone.localdate()]).aggregate(Sum('jumlah'))['jumlah__sum']
            period_demand = monthly_demand//3

            if current_stock <= period_demand or current_stock <= 15:
                flagged_items.append({'nama': str(record), 'stock': current_stock, 'demand': period_demand})


    # ADMIN SESSIONS
    list_session = []
    tunai = 0
    transfer = 0
    for row in session.objects.filter(date__range=[mulai, sampai], end_time__isnull=False).order_by('-date'):
        list_session.append(row)

    for row in transaksi.objects.filter(tanggal_pembayaran__range=[mulai, sampai]):
        my_total = row.item_dalam_transaksi.all().aggregate(total=Sum(F('jumlah') * F('harga')))['total']
        my_total = int(0 if my_total is None else my_total)
        if row.metode_pembayaran == 'Tunai':
            tunai += my_total
        else:
            transfer += my_total

    list_tr = list(zip(query_transaksi, list_item_transaksi, status, total_harga))
    list_msk = list(zip(query_masuk, list_item_masuk))
    list_klr = list(zip(query_keluar, list_item_keluar))
    context = {
        "total_value_tr": total_value_tr,
        "flagged_items": flagged_items,
        "list_session": list_session,
        "tunai": tunai,
        "transfer": transfer,
        "list_transaksi": list_tr,
        "item_terjual": sorted(item_terjual.values(), key=lambda x: x['jumlah'], reverse=True),
        "list_masuk": list_msk,
        "item_masuk": sorted(sum_item_masuk.values(), key=lambda x: x['gudang']),
        "list_keluar": list_klr,
        "item_keluar": sorted(sum_item_keluar.values(), key=lambda x: x['gudang']),
        "timeframe": timeframe
    }

    content = render_to_string('Inventory/get_recap.html', context)
    return JsonResponse({
        'content': content
    })


@login_required
def get_payment_dialog(request):
    my_id = request.GET.get('id')
    record = transaksi.objects.get(id=my_id)

    modal_content = render_to_string('Inventory/payment_dialog.html', {
        "transaksi": record,
    })
    return JsonResponse({'content': modal_content})
