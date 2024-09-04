from django.contrib import admin
from django.urls import path
from .views import HomeView, ResultView, DataView, PortfolioDetailView, PortfoliosView, Data

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('wallets/<str:name>', ResultView.as_view(), name='result'), 
    path('api/wallets/<str:name>', PortfolioDetailView.as_view(), name='api'), 
    path('api/wallets/', PortfoliosView.as_view(), name='api'), 
    path('api/data/', Data.as_view(), name='apiData'), 
    path('data/<str:assets>/', DataView.as_view(),  name='data'), 
]
