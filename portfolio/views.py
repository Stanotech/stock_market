from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from .models import Asset, Portfolio, PortfolioAsset
from rest_framework.response import Response
from portfolio.data_functions import *
from rest_framework import status
from .forms import AssetForm
from rest_framework import generics
from .serializers import *
from rest_framework.generics import ListCreateAPIView

@api_view(['GET', 'POST'])
def home(request):
    """
    Handles portfolio creation and related operations.
    """
    asset_form = AssetForm()

    if request.method == 'POST':
        selected_asset_names = request.data.get('selected_assets', [])
        portfolio_name = request.data.get('portfolio_name', 'My Portfolio')

        # Calculate Markowitz output
        mark_output = DataFunctions.markovitz(selected_asset_names)

        # Generate plots, save to files, and calculate max drawdown
        drawdown = DataFunctions.maximum_drawdown(
            DataFunctions.generate_plots(selected_asset_names, mark_output))

        # Create portfolio
        portfolio = Portfolio.objects.create(
            name=portfolio_name, risk=mark_output['exp_risk'], retur=mark_output['exp_ret'], max_drawdown=drawdown)

        # Add assets to portfolio
        for asset_name in selected_asset_names:
            asset = Asset.objects.get(name=asset_name)
            PortfolioAsset.objects.create(
                portfolio=portfolio, asset=asset, weight=mark_output[asset_name])

        # Pass output to result.html
        response_data = {'message': 'Portfolio created!'}

        return Response(response_data, status=status.HTTP_200_OK)

    # Get all assets from the database
    assets = Asset.objects.all()
    return render(request, 'form.html', {'assets': assets, 'asset_form': asset_form})


def result(request, name):
    """
    Displays the results of portfolio creation.
    """
    return render(request, 'result.html')


class PortfolioDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PortfolioSerializer

    def get_object(self):                       # function run automaticly with http request
        name = self.kwargs.get('name')          # getting portf name from request
        return Portfolio.objects.get(name=name) # get and return proper portfolio object using serializer

class PortfoliosView(ListCreateAPIView):
    serializer_class = PortfoliosSerializer

    def get_queryset(self):
        return Portfolio.objects.all()         