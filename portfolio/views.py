from django.shortcuts import render
from rest_framework import generics  # Import dla klas generycznych
from rest_framework.views import APIView  # Import dla APIView
from rest_framework.response import Response  # Import dla odpowiedzi API
from rest_framework import status  # Import statusów HTTP
from .models import Asset, Portfolio, PortfolioAsset  # Import modeli
from .forms import AssetForm  # Import formularza AssetForm
from .serializers import PortfolioSerializer, PortfoliosSerializer  # Import serializerów
from portfolio.data_functions import DataFunctions  # Import funkcji z modułu data_functions
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView  # Import ListCreateAPIView i RetrieveUpdateDestroyAPIView
import json  # Import modułu json dla pracy z danymi w formacie JSON


class HomeView(APIView):
    def get(self, request, *args, **kwargs):
        asset_form = AssetForm()
        assets = Asset.objects.all()
        return render(request, 'form.html', {'assets': assets, 'asset_form': asset_form})

    def post(self, request, *args, **kwargs):
        asset_form = AssetForm()
        selected_asset_names = request.data.get('selected_assets', [])
        portfolio_name = request.data.get('portfolio_name', 'My Portfolio')

        print(f"Selected assets: {selected_asset_names}")
        print(f"Portfolio name: {portfolio_name}")

        try:
            portfolio = Portfolio.objects.get(name=portfolio_name)
            return Response({'message': 'Portfolio already exists!'}, status=status.HTTP_409_CONFLICT)
        except Portfolio.DoesNotExist:
            # Kontynuacja procesu tworzenia portfela
            mark_output = DataFunctions.markovitz(selected_asset_names)

            # Sprawdzenie wyniku mark_output
            print(f"Markowitz output: {mark_output}")

            if mark_output is None:
                return Response({'message': 'Markowitz calculation failed'}, status=status.HTTP_400_BAD_REQUEST)

            drawdown = DataFunctions.maximum_drawdown(
                DataFunctions.generate_plots(selected_asset_names, mark_output, portfolio_name))

            portfolio = Portfolio.objects.create(
                name=portfolio_name, risk=mark_output['exp_risk'], retur=mark_output['exp_ret'], max_drawdown=drawdown)

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

class DataView(APIView):
    """
    Displays data of assets.
    """
    def get(self, request, assets):
        return render(request, 'data.html')

class PortfolioDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PortfolioSerializer

    def get_object(self):
        name = self.kwargs.get('name')
        return Portfolio.objects.get(name=name)

class PortfoliosView(ListCreateAPIView):
    serializer_class = PortfoliosSerializer

    def get_queryset(self):
        return Portfolio.objects.all()         

class Data(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PortfoliosSerializer

    def get(self, request, *args, **kwargs):
        assets = self.request.query_params.get('assets')
        assets = assets.split("&")
        mp = DataFunctions.prepare_data(assets).reset_index().set_index("Month")
        mp = mp.sort_values(by="Month")

        data = []
        for index, row in mp.iterrows():
            date = index
            values = row.tolist()[1:]
            data.append({'month': date, 'values': values})

        return Response(json.loads(json.dumps(data)), status=status.HTTP_200_OK)
