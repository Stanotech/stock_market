# assets/views.py
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Asset, Portfolio, PortfolioAsset
from .serializers import AssetSerializer
from django.db import transaction

@api_view(['GET'])
def get_assets(request):
    assets = Asset.objects.all()
    serializer = AssetSerializer(assets, many=True)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
def form(request):
    if request.method == 'POST':
        selected_assets = request.data.get('selected_assets', [])
        portfolio_name = request.data.get('portfolio_name', 'My Portfolio')

        # Tworzenie nowego portfela
        with transaction.atomic():
            portfolio = Portfolio.objects.create(name=portfolio_name)

            # Dodawanie wybranych aktywów do portfela
            total_weight = 100.0  # Całkowita waga musi wynosić 100%
            for asset_data in selected_assets:
                asset_name, weight = asset_data.split(':')
                asset = Asset.objects.get(name=asset_name)
                weight = float(weight)
                total_weight -= weight  # Redukcja dostępnej wagi
                PortfolioAsset.objects.create(portfolio=portfolio, asset=asset, weight=weight)

            # Jeśli waga nie wynosi 100%, cofnij transakcję
            if total_weight != 0:
                transaction.set_rollback(True)

        return Response({'message': 'Portfel został utworzony pomyślnie!'})

    return render(request, 'form.html')