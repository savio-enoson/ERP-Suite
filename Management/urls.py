from django.urls import include, path
from django.shortcuts import render, redirect
from . import views

app_name = "Management"

urlpatterns = [
    path("", views.index, name="index"),
]