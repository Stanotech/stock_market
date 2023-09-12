from django.shortcuts import render
from rest_framework.decorators import api_view
from .models import Asset, Portfolio, PortfolioAsset
from rest_framework.response import Response
from portfolio.data_functions import *
from rest_framework import status

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
        DataFunctions.generate_plots(selected_assets, mark_output)
        response_data = {'message': 'Portfel został utworzony pomyślnie!'}
        return Response(response_data, status=status.HTTP_200_OK)

    # Pobieranie wszystkich aktywów z bazy danych
    assets = Asset.objects.all()

    return render(request, 'form.html', {'assets': assets})


def result(request):
    
    return render(request, 'result.html', {'message': 'portfel utworzony pomyślnie!'})