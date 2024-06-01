from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.login_view, name='login'),
    path('login_verify/', views.login_verify, name='login_verify'),
    path('index/', views.index, name='index'),
    path('dashboard/', views.get_dashboard, name='dashboard'),
    path('logout/', views.logout, name='logout'),
    path('end_session/', views.end_session, name='end_session'),

    path('inventory/', include("Inventory.urls")),
    path('purcashing/', include("Purchasing.urls")),
    path('sales/', include("Sales.urls")),
    path('management/', include("Management.urls")),
]
