from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from .models import Asset, Portfolio, PortfolioAsset
from rest_framework.response import Response
from portfolio.data_functions import *
from rest_framework import status
from .forms import AssetForm
from rest_framework import generics
from .serializers import *

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

# @api_view(['GET', 'POST'])
# def edit(request):
#     if request.method == 'GET':


def result(request, name):
    """
    Displays the results of portfolio creation.
    """
    # mark_output = request.session.get('mark_output')
    # selected_asset_names = request.session.get('selected_asset_names')
    # max_drawdown = request.session.get('max_drawdown')
    # weights, parameters = [], []

    # for asset_name in selected_asset_names:
    #     weight_str = f"Weight for {asset_name} asset is {mark_output[asset_name]}"
    #     weights.append(weight_str)

    # exp_risk = mark_output.get("exp_risk", 0)
    # exp_ret = mark_output.get("exp_ret", 0)
    # parameters = f"Risk for this portfolio is {exp_risk:.2f}%\nExpected return of this portfolio is {exp_ret:.2f}%"

    return render(request, 'result.html')


class PortfolioDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PortfolioSerializer

    def get_object(self):
        name = self.kwargs.get('name')
        return Portfolio.objects.get(name=name)

