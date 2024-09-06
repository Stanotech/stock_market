import json 
from django.shortcuts import render


# Django Rest Framework (DRF) imports
from rest_framework import generics, status
from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

# Application-specific imports
from .models import Asset, Portfolio, PortfolioAsset
from .forms import AssetForm
from .serializers import PortfolioSerializer, PortfoliosSerializer
from portfolio.data_functions import DataFunctions


class HomeView(APIView):
    def get(self, request, *args, **kwargs):
        asset_form = AssetForm()
        assets = Asset.objects.all()
        return render(request, 'form.html', {'assets': assets, 'asset_form': asset_form})

    def post(self, request, *args, **kwargs):
        selected_asset_names = request.data.get('selected_assets', [])
        portfolio_name = request.data.get('portfolio_name', 'My Portfolio')

        # Form validation
        if not selected_asset_names:
            return Response({'message': 'No assets selected'}, status=status.HTTP_400_BAD_REQUEST)

        if not portfolio_name:
            return Response({'message': 'Portfolio name is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Checking does portfolio with that name exist
            portfolio = Portfolio.objects.get(name=portfolio_name)
            return Response({'message': 'Portfolio already exists!'}, status=status.HTTP_409_CONFLICT)
        
        except Portfolio.DoesNotExist:
            # Markowivz calculation
            mark_output = DataFunctions.markovitz(selected_asset_names)
            print(mark_output)

            if mark_output is None:
                return Response({'message': 'Markowitz calculation failed'}, status=status.HTTP_400_BAD_REQUEST)

            # Generating plots and max drawdown
            drawdown = DataFunctions.maximum_drawdown(
                DataFunctions.generate_plots(selected_asset_names, mark_output, portfolio_name))

            # Creating portfolio
            portfolio = Portfolio.objects.create(
                name=portfolio_name, risk=mark_output['exp_risk'], retur=mark_output['exp_ret'], max_drawdown=drawdown)
            
            # Adding assets to portfolio
            for asset_name in selected_asset_names:
                asset = Asset.objects.get(name=asset_name)
                PortfolioAsset.objects.create(
                    portfolio=portfolio, asset=asset, weight=mark_output[asset_name])

            return Response({'message': 'Portfolio created!'}, status=status.HTTP_200_OK)



class ResultView(APIView):
    """
    Displays the results of portfolio creation.
    """
    def get(self, request, name):
        return render(request, 'result.html')

class PortfolioDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PortfolioSerializer

    def get_object(self):
        name = self.kwargs.get('name')
        return Portfolio.objects.get(name=name)

class PortfoliosView(ListCreateAPIView):
    serializer_class = PortfoliosSerializer

    def get_queryset(self):
        return Portfolio.objects.all()         

class Data(generics.RetrieveAPIView):
    """
    Provides data of selected assets via API.
    """
    def get(self, request, *args, **kwargs):
        # Pobranie aktywów z parametrów zapytania
        assets = self.request.query_params.get('assets')
        
        if not assets:
            return Response({'message': 'No assets provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        assets = assets.split(",")
        mp = DataFunctions.prepare_data(assets).reset_index().set_index("Month")
        mp = mp.sort_values(by="Month")

        # Przygotowanie danych do zwrócenia
        data = []
        for index, row in mp.iterrows():
            date = index
            values = row.tolist()[1:]
            data.append({'month': date, 'values': values})

        return Response(json.loads(json.dumps(data)), status=status.HTTP_200_OK)
    
class DataPageView(APIView):
    """
    Displays the data page (data.html) without requiring any additional arguments.
    """
    def get(self, request, *args, **kwargs):
        return render(request, 'data.html')