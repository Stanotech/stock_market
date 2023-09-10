import os
import csv
import pandas as pd
from datetime import datetime
from portfolio.models import Asset, AssetValue
from django.db.models import Max, Min
import numpy as np
from cvxpy import *

class DataFunctions:

    @classmethod
    def import_data(cls):
        data_folder = 'data'  # Name of the data folder
        files = sorted(os.listdir(data_folder))
        for file_name in files:
            print(file_name)
            try:
                if file_name.endswith('.txt'):
                    file_path = os.path.join(data_folder, file_name)

                    with open(file_path, 'r') as csv_file:
                        csv_reader = csv.DictReader(csv_file)
                        asset_name = file_name.split('.')[0]

                        # Creating a new asset if it doesn't exist
                        asset, created = Asset.objects.get_or_create(name=asset_name)

                        # Creating an empty DataFrame to store data from the CSV file
                        data = []

                        # Iterating through the rows of the CSV file
                        for row in csv_reader:
                            
                            date = datetime.strptime(row['<DATE>'], '%Y%m%d').date()
                            value = float(row['<CLOSE>'])
                            data.append({'date': date, 'value': value})

                        # Creating a DataFrame from the loaded data
                        df = pd.DataFrame(data)
                        # Ensure the 'date' column is converted to date type
                        df['date'] = pd.to_datetime(df['date'])

                        # Calculating the average asset value for each month
                        monthly_avg = df.groupby(df['date'].dt.strftime('%Y-%m'))['value'].mean()

                        # Iterating through the calculated average values and saving them to the database
                        for index, avg_value in monthly_avg.items():
                            year_month = datetime.strptime(index, '%Y-%m').date()

                            # Creating or updating the value for the asset in that month
                            asset_value, created = AssetValue.objects.update_or_create(
                                asset=asset,
                                date=year_month,
                                defaults={'value': avg_value}
                            )

                        print(f'Successfully imported data for {asset_name}')
                        
            except Exception as e:
                # Place exception handling code here, e.g., printing error information
                print(f"An error occurred: {e}")
                continue

    @classmethod
    def PrepareData(cls, assets_input):
        selected_assets = assets_input  # Replace with the actual asset names
        assets = Asset.objects.filter(name__in=selected_assets)

        # Inicjalizacja pustego słownika, który będzie przechowywać dane
        data = {'Date': []}

        # Utworzenie listy dat dla wybranych aktywów
        date_ranges = [AssetValue.objects.filter(asset=asset).values_list('date', flat=True)
                       for asset in assets]
        

        # Znalezienie wspólnego zakresu dat
        common_dates = set(date_ranges[0]).intersection(*date_ranges[1:])

        # Jeśli brak wspólnych dat, zakończ funkcję
        if not common_dates:
            return None

        # Dodawanie dat do słownika
        data['Date'] = list(common_dates)

        # Dodawanie wartości dla każdego aktywa
        for asset in assets:
            values = AssetValue.objects.filter(asset=asset, date__in=common_dates).order_by('date')
            data[asset.name] = [value.value for value in values]

        

        df = pd.DataFrame(data)
        # Konwertuj kolumnę "Date" na typ daty
        df['Date'] = pd.to_datetime(df['Date'])
    
        # Dodaj kolumnę "Month" na podstawie daty
        df['Month'] = df['Date'].dt.strftime('%Y-%m')

        # Changing Month column position to first
        date_column = df.pop('Month')
        df.insert(0, 'Month', date_column)

        df.drop(columns=["Date"], inplace=True)
        
        print(df)
        return df
    
    @classmethod
    def Markovitz(cls, assets_input):
    
        mp = DataFunctions.PrepareData(assets_input)
        print(mp)
        mr = pd.DataFrame()


        # compute monthly returns

        for s in mp.columns:
            date = mp["Month"][0]
            print(f"date {date}")
            pr0 = mp[s][date] 
            print(pr0)
            for t in range(1,len(mp.index)):
                date = mp.index[t]
                pr1 = mp[s][date]
                ret = (pr1-pr0)/pr0
                mr._set_value(date,s,ret)
                pr0 = pr1


        r = np.asarray(np.mean(mr, axis=0))
        C = np.asmatrix(np.cov(mr, rowvar=False))

        print(f"mrooooooooo {mr}")
        # Get symbols
        symbols = mr.columns
        print(f"msymmomomo  {symbols}")

        # Number of variables
        n = len(symbols)

        # The variables vector
        x = Variable(n)

        # The minimum return
        req_return = 0.02

        # The return
        ret = r.T@x

        # The risk in xT.Q.x format
        risk = quad_form(x, C)

        # The core problem definition with the Problem class from CVXPY
        prob = Problem(Minimize(risk), [sum(x)==1, ret >= req_return, x >= 0])

   
   
        try:
            prob.solve()
            output ={}
            for idx, s in enumerate(symbols):
                print(f"chujumuju  {s}  {idx}")
                print(x.value)
                print(round(100*x.value[idx],2))
                output[s] = round(100*x.value[s],2)
            output['exp_ret'] = round(100*ret.value,2)
            output['exp_risk'] = round(100*risk.value**0.5,2)
            print("sucess")
            return output
        except Exception as e:
            print("errorrror")
            print (e)