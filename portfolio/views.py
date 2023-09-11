# assets/views.py
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
        portfolio_name = request.data.get('portfolio_name', 'My Portfolio')

        # Creating portfolio
        portfolio = Portfolio.objects.create(name=portfolio_name)

        # Markovitz calculation
        mark_output = DataFunctions.Markovitz(selected_assets)

        # Adding assets to portfolio
        for asset_name in selected_assets:
            asset = Asset.objects.get(name=asset_name)
            PortfolioAsset.objects.create(portfolio=portfolio, asset=asset, weight=mark_output[asset_name])

        # Generowanie wykresów
        plot1, plot2, plot3 = DataFunctions.generate_plots(selected_assets, mark_output)

        return render(request, 'result.html', {'message': 'Portfel został utworzony pomyślnie!', 'plot1': plot1, 'plot2': plot2, 'plot3': plot3})

    # Getting all assets from database
    assets = Asset.objects.all()

    return render(request, 'form.html', {'assets': assets})

