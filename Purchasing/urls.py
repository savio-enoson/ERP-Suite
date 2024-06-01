from django.urls import include, path
from django.shortcuts import render, redirect
from . import views

app_name = "Purchasing"

urlpatterns = [
    path("", views.riwayat_purchase_order, name="index"),
    path("get_po/", views.get_po, name="get_po"),
    path("get_barang_masuk/", views.get_barang_masuk, name="get_barang_masuk"),
    path("get_pengiriman/", views.get_pengiriman, name="get_pengiriman"),
    path("modify_po/", views.modify_po, name="modify_po"),
    path("post_po/", views.post_po, name="post_po"),
    path("modify_pengiriman/", views.modify_pengiriman, name="modify_pengiriman"),
    path("post_pengiriman/", views.post_pengiriman, name="post_pengiriman"),
    path("terima_pengiriman/", views.terima_pengiriman, name="terima_pengiriman"),
    path("post_barang_masuk/", views.post_barang_masuk, name="post_barang_masuk"),
    path("riwayat_barang_masuk/", views.riwayat_barang_masuk, name="riwayat_barang_masuk"),
    path("riwayat_pengiriman/", views.riwayat_pengiriman, name="riwayat_pengiriman"),
]