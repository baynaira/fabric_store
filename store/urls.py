from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.store, name='store'),
    path('checkout/', views.checkout, name='checkout'),
    path('manage_stock/', views.manage_stock, name='manage_stock'),
    path('upload_products/', views.upload_products, name='upload_products'),
    path('export_products/', views.export_products, name='export_products'),
]
