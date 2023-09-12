# Generated by Django 4.2.4 on 2023-09-02 22:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='PortfolioAsset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.FloatField()),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio.asset')),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio.portfolio')),
            ],
        ),
        migrations.AddField(
            model_name='portfolio',
            name='assets',
            field=models.ManyToManyField(through='portfolio.PortfolioAsset', to='portfolio.asset'),
        ),
        migrations.CreateModel(
            name='AssetValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('value', models.FloatField()),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio.asset')),
            ],
        ),
    ]