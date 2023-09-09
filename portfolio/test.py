from portfolio.models import Asset, AssetValue

# Get all assets
assets = Asset.objects.all()

# Iterate through assets
for asset in assets:
    print(f"Asset: {asset.name}")
    
    # Get all values for a specific asset
    asset_values = AssetValue.objects.filter(asset=asset)
    
    # Iterate through values for the specific asset
    for asset_value in asset_values:
        print(f"  Date: {asset_value.date}, Value: {asset_value.value}")

    print("\n")