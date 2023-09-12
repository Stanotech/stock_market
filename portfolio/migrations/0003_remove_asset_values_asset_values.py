# Generated by Django 4.2.4 on 2023-09-04 19:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0002_remove_assetvalue_asset_asset_values'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asset',
            name='values',
        ),
        migrations.AddField(
            model_name='asset',
            name='values',
            field=models.OneToOneField(default=0, on_delete=django.db.models.deletion.CASCADE, to='portfolio.assetvalue'),
        ),
    ]