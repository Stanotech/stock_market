from rest_framework import serializers
from .models import *

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['name']

class PortfolioAssetSerializer(serializers.ModelSerializer):
    asset = AssetSerializer(many=False, read_only=True)

    class Meta:
        model = PortfolioAsset
        fields = ['asset', 'weight']

class PortfolioSerializer(serializers.ModelSerializer):
    asset_weights = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = ['name', 'asset_weights', 'risk', 'retur', 'max_drawdown']

    def get_asset_weights(self, obj):
        asset_weights = PortfolioAsset.objects.filter(portfolio=obj)
        serialized_data = PortfolioAssetSerializer(asset_weights, many=True).data
        return serialized_data

class PortfoliosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ['name']
