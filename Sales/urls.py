from django.urls import include, path
from django.shortcuts import render, redirect
from . import views

app_name = "Sales"

urlpatterns = [
    path("", views.transaction_records, name="index"),
    path("mofidy_transaksi/", views.mofidy_transaksi, name="mofidy_transaksi"),
    path("post_transaksi/", views.post_transaksi, name="post_transaksi"),
    path("get_transaksi/", views.get_transaksi, name="get_transaksi"),
    path("get_barang_keluar/", views.get_barang_keluar, name="get_barang_keluar"),
    path("create_bill/", views.create_bill, name="create_bill"),
    path("get_bill/", views.get_bill, name="get_bill"),
    path("riwayat_barang_keluar/", views.riwayat_barang_keluar, name="riwayat_barang_keluar"),
    path("keluarkan_barang/", views.keluarkan_barang, name="keluarkan_barang"),
    path("post_barang_keluar/", views.post_barang_keluar, name="post_barang_keluar"),
    path("get_print_dialog/", views.get_print_dialog, name="get_print_dialog"),
    path("post_print_req/", views.post_print_req, name="post_print_req"),
]