# assets/views.py
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from .models import Asset, Portfolio, PortfolioAsset
from .serializers import AssetSerializer
from rest_framework.response import Response

@api_view(['GET', 'POST'])
def home(request):
    if request.method == 'POST':
        selected_assets = request.data.get('selected_assets', [])
        portfolio_name = request.data.get('portfolio_name', 'My Portfolio')

        # Tworzenie nowego portfela
        portfolio = Portfolio.objects.create(name=portfolio_name)

        # Dodawanie wybranych aktywów do portfela
        for asset_name in selected_assets:
            asset = Asset.objects.get(name=asset_name)
            PortfolioAsset.objects.create(portfolio=portfolio, asset=asset)

        return Response({'message': 'Portfel został utworzony pomyślnie!'})

    return render(request, 'form.html')