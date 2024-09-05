from django.contrib import admin
from django.urls import path
from .views import HomeView, ResultView, PortfolioDetailView, PortfoliosView, Data, DataPageView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('wallets/<str:name>/', ResultView.as_view(), name='result'), 
    path('api/wallets/<str:name>/', PortfolioDetailView.as_view(), name='api'), 
    path('api/wallets/', PortfoliosView.as_view(), name='api'), 
    path('api/data/', Data.as_view(), name='apiData'),  # API to fetch data
    path('data/', DataPageView.as_view(), name='data'),  # Widok, który zwraca stronę data.html
]

