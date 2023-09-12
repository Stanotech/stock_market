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
        request.session['mark_output'] = mark_output
        request.session['selected_assets'] = selected_assets
        return Response(response_data, status=status.HTTP_200_OK)

    # Pobieranie wszystkich aktywów z bazy danych
    assets = Asset.objects.all()

    return render(request, 'form.html', {'assets': assets})


def result(request):
    mark_output = request.session.get('mark_output')
    selected_assets = request.session.get('selected_assets')
    weights, parameters = [], []
    for asset in selected_assets:
        weight_str = f"Weight for {asset} asset is {mark_output[asset]}"
        weights.append(weight_str)

    exp_risk = mark_output["exp_risk"]
    exp_ret = mark_output["exp_ret"]
    parameters = f"Risk for this portfolio is {exp_risk}% \n Expected return of this portfolio is {exp_ret}%"


    return render(request, 'result.html', 
                  {'message': 'portfel utworzony pomyślnie!', 'parameters': parameters, 
                   'weights': weights})


        
