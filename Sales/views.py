from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from django.utils.formats import date_format, time_format
from django.utils.timezone import localdate
import datetime
import json

from django.db.models import Sum, Min, Q, F
from django.db.models.functions import Coalesce

from .models import transaksi, item_transaksi, print_request
from Inventory.models import stack, item_keluar, keluar_gudang, gudang


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
def transaction_records(request):
    timeframe = [localdate() - datetime.timedelta(60), localdate()]

    query = transaksi.objects.filter(tanggal__range=timeframe).order_by('-tanggal', '-waktu')
    status = []
    total_harga = []

    for row in query:
        my_total = row.item_dalam_transaksi.all().aggregate(total=Sum(F('jumlah') * F('harga')))['total']
        my_total = int(0 if my_total is None else my_total)
        total_harga.append(my_total)

        status.append(map_status(row.status, row.status_pembayaran))

    context = {
        "header": "Riwayat Transaksi",
        "riwayat": zip(query, status, total_harga)
    }

    page_content = render_to_string('Sales/index.html', context)

    return JsonResponse({
        'content': page_content,
        'title': 'Sales | Riwayat Transaksi',
        'heading': 'Sales'
    })


@login_required
def mofidy_transaksi(request):
    my_id = request.GET.get('id')
    my_record = transaksi.objects.get(id=my_id) if my_id else {
        "id": None, "pelanggan": "", "pembayaran": "Cash",
        "status_pembayaran": False, "status": False, "keterangan": ""
    }

    record_items = []
    if my_id != '':
        for row in my_record.item_dalam_transaksi.all():
            record_items.append({
                "id": row.item.id,
                "nama": row.item.nama,
                "jumlah": row.jumlah,
                "harga": row.harga,
                "harga_total": row.jumlah * row.harga,
                "keterangan": "" if row.keterangan is None else row.keterangan
            })

    modal_content = render_to_string('Sales/modify_transaksi.html', {
        "transaksi": my_record,
        "item_transaksi": json.dumps(record_items) if my_id != '' else None
    })
    return JsonResponse({'content': modal_content})


@login_required
def post_transaksi(request):
    id_transaksi = request.POST.get('id_transaksi')
    pelanggan = request.POST.get('pelanggan').title()
    pembayaran = request.POST.get('pembayaran').split(" - ")
    keterangan = request.POST.get('keterangan')
    keterangan = None if keterangan == "" else keterangan

    status_pembayaran = True if "Cash" in pembayaran else False
    status = True if "Toko" in pembayaran else False

    item_dalam_transaksi = json.loads(request.POST.get('item_transaksi'))

    target_item = None

    if id_transaksi != "None":
        target_item = transaksi.objects.get(id=id_transaksi)
        updating = True
    else:
        updating = False

    if updating:
        target_item.pelanggan = pelanggan
        try:
            target_item.pembayaran = f"{pembayaran[0]} - {pembayaran[2]}"
            target_item.metode_pembayaran = pembayaran[1]
            target_item.tanggal_pembayaran = timezone.localtime()
        except:
            target_item.pembayaran = f"{pembayaran[0]} - {pembayaran[1]}"
        target_item.keterangan = keterangan
        target_item.status = status
        target_item.status_pembayaran = status_pembayaran

        target_item.save()
    else:
        target_item = transaksi(pelanggan=pelanggan, status=status, status_pembayaran=status_pembayaran, keterangan=keterangan,
                                pembayaran=f"{pembayaran[0]} - {pembayaran[2]}" if status_pembayaran else f"{pembayaran[0]} - {pembayaran[1]}",
                                metode_pembayaran=pembayaran[1] if status_pembayaran else None,
                                tanggal_pembayaran=timezone.localtime() if status_pembayaran else None
                                )
        target_item.save()

    if updating:
        target_item.item_dalam_transaksi.all().delete()

    for row in item_dalam_transaksi:
        new_item = item_transaksi(transaksi=target_item, item_id=row['id'], jumlah=row['jumlah'], harga=row['harga'],
                                  keterangan="" if row['keterangan'] is None else row['keterangan'])
        new_item.save()

    return JsonResponse({
        'message': f"Berhasil mengubah {target_item}" if updating else f"Berhasil menambahkan {target_item}"
    })


@login_required
def get_transaksi(request):
    my_id = request.GET.get('id')

    my_record = transaksi.objects.get(id=my_id)
    my_items = my_record.item_dalam_transaksi.all()

    try:
        d_pembayaran = f"{my_record.metode_pembayaran} - {date_format(my_record.tanggal_pembayaran)}"
    except:
        d_pembayaran = "Belum Dibayar"

    context = {
        "transaksi": {
            "id": my_id,
            "pembayaran": my_record.pembayaran,
            "d_pembayaran": d_pembayaran,
            "header": f"{my_record.pelanggan} | {date_format(my_record.tanggal)}, "
                      f"{time_format(my_record.waktu)} | Admin: {my_record.admin.username}",
            "status": map_status(my_record.status, my_record.status_pembayaran),
            "keterangan": my_record.keterangan
        },
        "item_transaksi": my_items,
        "grand_total": my_items.aggregate(total=Sum(F('jumlah') * F('harga')))['total'],
        "ada_keterangan": my_items.exclude(keterangan__exact='').exclude(keterangan__isnull=True).exists()
    }

    modal_content = render_to_string('Sales/get_transaksi.html', context)
    return JsonResponse({'content': modal_content})


@login_required
def get_barang_keluar(request):
    my_id = request.GET.get('id')
    type = request.GET.get('type')

    # Buffer values
    my_transaksi = None
    my_object = None
    barang_keluar = []

    # Get all from parent
    if type == '0':
        my_transaksi = transaksi.objects.get(id=my_id)

        for row in my_transaksi.record_keluar.all():
            buffer = {
                "record": row,
                "items": row.item_dalam_record_keluar.all()
            }
            barang_keluar.append(buffer)
    # Get object by id
    elif type == '1':
        my_object = item_keluar.objects.get(id=my_id).parent
        my_transaksi = my_object.transaksi

        barang_keluar.append({
            "record": my_object,
            "items": my_object.item_dalam_record_keluar.all()
        })

    context = {
        "id": my_transaksi.id,
        "type": type,
        "header": f"{my_transaksi.pelanggan} | {date_format(my_transaksi.tanggal)}, {time_format(my_transaksi.waktu)}",
        "item_keluar": barang_keluar
    }

    modal_content = render_to_string('Sales/get_barang_keluar.html', context)
    return JsonResponse({'content': modal_content})


@login_required
def create_bill(request):
    context = {
        "default_start": date_format(localdate() - datetime.timedelta(days=30), 'Y-m-01')
    }

    page_content = render_to_string('Sales/create_bill.html', context)

    return JsonResponse({
        'content': page_content,
        'title': 'Sales | Buat Tagihan',
        'heading': 'Sales'
    })


@login_required
def get_bill(request):
    pelanggan = request.GET.get('pelanggan')
    mulai = request.GET.get('mulai')
    sampai = request.GET.get('sampai')

    list_item = []
    list_total = []

    list_transaksi = transaksi.objects.filter(pelanggan__contains=pelanggan,
                                              tanggal__range=[mulai, sampai]).order_by('-tanggal', '-waktu')

    list_hari = list_transaksi.values('tanggal').annotate(harga_total=
                                                          Coalesce(Sum(F('item_dalam_transaksi__jumlah') * F(
                                                              'item_dalam_transaksi__harga')), 0)).order_by('tanggal')

    for row in list_transaksi:
        list_item.append(row.item_dalam_transaksi.all())
        list_total.append(row.item_dalam_transaksi.all().aggregate(total=Sum(F('jumlah') * F('harga')))['total'])

    context = {
        "list_transaksi": zip(list_transaksi, list_item, list_total),
        "list_hari": list_hari,
        "grand_total": list_hari.aggregate(total=Sum('harga_total'))['total']
    }

    content = render_to_string('Sales/get_bill.html', context)
    return JsonResponse({
        'content': content
    })


@login_required
def riwayat_barang_keluar(request):
    context = {
        "header": "Riwayat Barang Keluar",
        "riwayat": keluar_gudang.objects.all().order_by('-tanggal', '-waktu')[:200]
    }

    page_content = render_to_string('Sales/riwayat_barang_keluar.html', context)

    return JsonResponse({
        'content': page_content,
        'title': 'Sales | Riwayat Barang Keluar',
        'heading': 'Sales'
    })


@login_required
def keluarkan_barang(request):
    my_id = request.GET.get('id')

    my_record = transaksi.objects.get(id=my_id)

    available_gudang = []
    list_item_transaksi = []
    for row in my_record.item_dalam_transaksi.all():
        list_item_transaksi.append({"id": row.id, "parent_id": row.item.id,
                                    "nama": str(row.item), "jumlah": row.jumlah})

        temp_list = []
        for i in row.item.barang_dalam_stack.all():
            temp_list.append({"id": i.gudang_id, "nama": f"{i.gudang.nama} ({i.jumlah})"})

        available_gudang.append(temp_list)

    modal_content = render_to_string('Sales/keluarkan_barang.html', {
        "transaksi": my_record,
        "list_gudang": gudang.objects.all(),
        "item_transaksi": zip(list_item_transaksi, available_gudang),
        "list_item": my_record.item_dalam_transaksi.all()
    })
    return JsonResponse({'content': modal_content})


@login_required
def post_barang_keluar(request):
    id_transaksi = request.POST.get('id_transaksi')

    list_item_keluar = json.loads(request.POST.get('item_keluar'))
    target_item = keluar_gudang(transaksi_id=id_transaksi)
    target_item.save()

    for item in list_item_keluar:
        target_stack = stack.objects.get(item_id=item['item_parent_id'], gudang_id=item['gudang_id'])

        new_item = item_keluar(parent=target_item, item_parent_id=item['item_parent_id'],
                               item_id=item['item_id'], gudang_id=item['gudang_id'],
                               jumlah=item['jumlah'], jumlah_awal=target_stack.jumlah)
        new_item.save()

        target_stack.keterangan = None if item['keterangan'] == "" else item['keterangan']
        target_stack.jumlah -= item['jumlah']
        target_stack.save()

    return JsonResponse({
        'message': f"Berhasil menambahkan {target_item}"
    })


@login_required
def get_print_dialog(request):
    my_id = request.GET.get('id')
    record = transaksi.objects.get(id=my_id)

    modal_content = render_to_string('Sales/print_dialog.html', {
        "transaksi": record,
        "harga_total": record.item_dalam_transaksi.all().aggregate(total=Sum(F('jumlah') * F('harga')))['total']
    })
    return JsonResponse({'content': modal_content})


@login_required
def post_print_req(request):
    id_transaksi = request.POST.get('id_transaksi')
    nominal_bayar = request.POST.get('nominal_bayar')
    printer_key = request.POST.get('printer_key')

    new_req = print_request(transaksi_id=id_transaksi, nominal_bayar=nominal_bayar, printer_key=printer_key)
    new_req.save()
    return JsonResponse({'status': 1})
