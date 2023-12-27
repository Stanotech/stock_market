from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('wallets/<str:name>', views.result, name='result'), 
    path('api/wallets/<str:name>', views.PortfolioDetailView.as_view(), name='api'), 
    path('api/wallets/', views.PortfoliosView.as_view(), name='api'), 
]
