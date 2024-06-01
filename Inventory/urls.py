from django.urls import include, path
from django.shortcuts import render, redirect
from . import views

app_name = "Inventory"

urlpatterns = [
    path("", views.get_inventory, name="index"),
    path("modify_item/", views.modify_item, name="modify_item"),
    path("post_item/", views.post_item, name="post_item"),
    path("get_stack/", views.get_stack, name="get_stack"),
    path("get_item_list/", views.get_item_list, name="get_item_list"),
    path("get_item_stock/", views.get_item_stock, name="get_item_stock"),
    path("stock_gudang/", views.stock_gudang, name="stock_gudang"),
    path("modify_stack/", views.modify_stack, name="modify_stack"),
    path("post_stack/", views.post_stack, name="post_stack"),
    path("lunaskan/", views.lunaskan, name="lunaskan"),
    path("selesaikan/", views.selesaikan, name="selesaikan"),
    path("kembali_ke_draft/", views.kembali_ke_draft, name="kembali_ke_draft"),
    path("create_recap/", views.create_recap, name="create_recap"),
    path("get_recap/", views.get_recap, name="get_recap"),
    path("get_payment_dialog/", views.get_payment_dialog, name="get_payment_dialog"),
]