from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.template.loader import render_to_string

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from Sales.views import map_status
from django.db.models import Sum, Min, Q, F

from Management.models import session
from Sales.models import transaksi
from Inventory.models import masuk_gudang, keluar_gudang


@login_required
def index(request):
    return render(request, 'General/index.html', {
        "content": get_dashboard(request, True)
    })


@login_required
def get_dashboard(request, no_json=False):
    query = transaksi.objects.filter(tanggal=timezone.localdate()).order_by('-tanggal', '-waktu')
    status = []
    total_harga = []

    for row in query:
        my_total = row.item_dalam_transaksi.all().aggregate(total=Sum(F('jumlah') * F('harga')))['total']
        my_total = int(0 if my_total is None else my_total)
        total_harga.append(my_total)

        status.append(map_status(row.status, row.status_pembayaran))

    context = {
        "list_transaksi": zip(query, status, total_harga),
        "list_masuk": masuk_gudang.objects.filter(tanggal=timezone.localdate()).order_by('-tanggal', '-waktu'),
        "list_keluar": keluar_gudang.objects.filter(tanggal=timezone.localdate()).order_by('-tanggal', '-waktu')
    }

    page_content = render_to_string('General/dashboard.html', context)

    if no_json:
        return page_content

    return JsonResponse({
        'content': page_content,
        'title': 'Dashboard',
        'heading': 'Dashboard'
    })


def login_verify(request):
    if request.user.is_authenticated:
        return redirect("index")

    username = request.POST.get("username", None)
    password = request.POST.get("password", None)
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        try:
            current_session = session.objects.get(admin=request.user, date=timezone.localdate())
        except:
            current_session = None

        if current_session:
            current_session.start_time = timezone.localtime()
            current_session.end_time = None
            current_session.cash_due = 0
            current_session.cash_taken = 0
            current_session.cash_received = 0
            current_session.keterangan = None
            current_session.save()
        else:
            new_session = session()
            new_session.save()

        return redirect("index")
    else:
        return render(request, 'General/login.html',
                      {"message": "Login gagal. Coba periksa ulang username dan password."})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("index")
    else:
        return render(request, 'General/login.html')


@login_required
def logout(request):
    last_session = session.objects.filter(admin=request.user).latest('date', 'start_time')

    context = {
        "session": last_session
    }

    modal_content = render_to_string('General/logout.html', context)
    return JsonResponse({'content': modal_content})


@login_required
@csrf_exempt
def end_session(request):
    current_session = session.objects.get(id=request.POST.get('session_id'))
    current_session.cash_received = request.POST.get('cash_diterima')
    current_session.cash_taken = request.POST.get('cash_diambil')
    current_session.end_time = request.POST.get('jam_selesai')
    current_session.keterangan = request.POST.get('keterangan')

    cash_due = 0
    transaksi_hari_ini = transaksi.objects.filter(status_pembayaran=True, metode_pembayaran="Tunai",
                                                  tanggal_pembayaran=current_session.date)

    for row in transaksi_hari_ini:
        for item in row.item_dalam_transaksi.all():
            cash_due += item.jumlah * item.harga

    current_session.cash_due = cash_due
    current_session.save()

    logout(request)
    request.session.flush()
    request.user = AnonymousUser
    return redirect("login")
