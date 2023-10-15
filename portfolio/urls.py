from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('wallets/<str:name>', views.result, name='result'), 
    # path('edit/', views.edit, name='edit'), 
]
