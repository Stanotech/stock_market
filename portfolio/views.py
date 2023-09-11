import os
from django.http import FileResponse
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from .models import Asset, Portfolio, PortfolioAsset
from .serializers import AssetSerializer
from rest_framework.response import Response
from portfolio.data_functions import *


@api_view(['GET', 'POST'])
def home(request):
    if request.method == 'POST':
        selected_assets = request.data.get('selected_assets', [])
        print(selected_assets)
        portfolio_name = request.data.get('portfolio_name', 'My Portfolio')

        # Tworzenie portfela
        portfolio = Portfolio.objects.create(name=portfolio_name)

        # Obliczenia związane z modelem Markovitza
        mark_output = DataFunctions.Markovitz(selected_assets)

        # Dodawanie aktywów do portfela
        for asset_name in selected_assets:
            asset = Asset.objects.get(name=asset_name)
            PortfolioAsset.objects.create(portfolio=portfolio, asset=asset, weight=mark_output[asset_name])

        # Generowanie wykresów i zapisywanie ich do plików
        plot1_path, plot2_path, plot3_path = DataFunctions.generate_plots(selected_assets, mark_output)

        print("madafaka")
        return render(
            request,
            'result.html',
            {
                'message': 'Portfel został utworzony pomyślnie!',
                'plot1_path': plot1_path,
                'plot2_path': plot2_path,
                'plot3_path': plot3_path,
            },
        )

    # Pobieranie wszystkich aktywów z bazy danych
    assets = Asset.objects.all()

    return render(request, 'form.html', {'assets': assets})