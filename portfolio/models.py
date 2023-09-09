from django.db import models

class Asset(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class AssetValue(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, default=None)
    date = models.DateField()
    value = models.FloatField()

    def __str__(self):
        return f"{self.date}"

class Portfolio(models.Model):
    name = models.CharField(max_length=50)
    assets = models.ManyToManyField(Asset, through='PortfolioAsset')

    def __str__(self):
        return self.name

class PortfolioAsset(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    weight = models.FloatField()

    def __str__(self):
        return f"{self.asset.name} ({self.weight}%)"
