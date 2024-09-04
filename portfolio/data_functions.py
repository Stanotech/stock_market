import os
import csv
import pandas as pd
from datetime import datetime
from portfolio.models import Asset, AssetValue
import numpy as np
from cvxpy import *
import matplotlib.pyplot as plt
import matplotlib
from io import BytesIO
import base64
import builtins
from django.conf import settings

matplotlib.use('agg')

PROJECT_DIR = settings.BASE_DIR

class DataFunctions:
    @classmethod
    def import_data(cls):
        """
        Import data from CSV files and save it to the database.

        This function reads CSV files from a specified directory, parses them,
        and stores the data in the database as asset values.

        Returns:
            None
        """
        data_folder = 'data'  # Name of the data folder
        files = sorted(os.listdir(data_folder))

        for file_name in files:
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
    def prepare_data(cls, assets_input):
        """
        Prepare and structure data for selected assets.

        This function takes a list of asset names as input and retrieves data
        for those assets from the database, organizing it into a structured DataFrame.

        Args:
            assets_input (list): A list of asset names to include in the analysis.

        Returns:
            pandas.DataFrame: A DataFrame containing organized asset data.
        """
        selected_assets = assets_input  # Replace with the actual asset names
        assets = Asset.objects.filter(name__in=selected_assets)

        # Initialize an empty dictionary to store data
        data = {'Date': []}

        # Create a list of dates for selected assets
        date_ranges = [AssetValue.objects.filter(asset=asset).values_list('date', flat=True)
                       for asset in assets]

        # Find common dates
        common_dates = sorted(set(date_ranges[0]).intersection(*date_ranges[1:]))
        common_dates = common_dates[-30:]

        # If there are no common dates, exit the function
        if not common_dates:
            return None

        # Add dates to the dictionary
        data['Date'] = list(common_dates)

        # Add values for each asset
        for asset in assets:
            values = AssetValue.objects.filter(asset=asset, date__in=common_dates).order_by('date')
            data[asset.name] = [value.value for value in values]

        df = pd.DataFrame(data)
        # Convert the "Date" column to date type
        df['Date'] = pd.to_datetime(df['Date'])

        # Add "Month" column
        df['Month'] = df['Date'].dt.strftime('%Y-%m')

        # Change Month column position to first
        date_column = df.pop('Month')
        df.insert(0, 'Month', date_column)
        df.drop(columns=["Date"], inplace=True)

        return df

    @classmethod
    def markovitz(cls, assets_input):
        """
        Perform Markowitz portfolio optimization.

        This function takes a list of asset names as input, retrieves their data,
        and performs Markowitz portfolio optimization to determine asset weights.

        Args:
            assets_input (list): A list of asset names to include in the analysis.

        Returns:
            dict: A dictionary containing asset weights and other portfolio statistics.
        """
        mp = DataFunctions.prepare_data(assets_input).set_index("Month")
        mp = mp.sort_values(by="Month")
        mr = pd.DataFrame()

        # Compute monthly returns
        for s in mp.columns:
            date = mp.index[0]
            pr0 = mp[s][date]
            for t in range(1, len(mp.index)):
                date = mp.index[t]
                pr1 = mp[s][date]
                ret = (pr1 - pr0) / pr0
                mr._set_value(date, s, ret)
                pr0 = pr1

        r = np.asarray(np.mean(mr, axis=0))
        C = np.asmatrix(np.cov(mr, rowvar=False))

        # Get symbols
        symbols = mr.columns

        # Number of variables
        n = len(symbols)

        # The variables vector
        x = Variable(n)

        # The minimum return
        req_return = 0.02

        # The return
        ret = r.T @ x

        # The risk in xT.Q.x format
        risk = quad_form(x, C)

        # The core problem definition with the Problem class from CVXPY
        prob = Problem(Minimize(risk), [sum(x) == 1, ret >= req_return, x >= 0])

        try:
            prob.solve()
            output = {}
            for idx, s in enumerate(symbols):
                output[s] = round(100 * x.value[idx], 2)
            output['exp_ret'] = round(100 * ret.value, 2)
            output['exp_risk'] = round(100 * risk.value**0.5, 2)
            return output
        except Exception as e:
            print("Error:")
            print(e)

    @classmethod
    def calculate_portfolio_values(cls, selected_assets, mark_output):
        """
        Calculate the portfolio values over time.

        This function calculates the values of a portfolio over time based on
        selected assets and their weights.

        Args:
            selected_assets (list): A list of selected asset names.
            mark_output (dict): A dictionary containing asset weights.

        Returns:
            numpy.ndarray: An array containing portfolio values over time.
        """
        mp = DataFunctions.prepare_data(selected_assets).set_index("Month")
        mp = mp.sort_values(by="Month")
        weights = [mark_output[asset_name] for asset_name in selected_assets]
        portfolio_values = np.sum(mp[selected_assets] * weights, axis=1)
        return portfolio_values

    @classmethod
    def get_plot_as_base64_string(cls, plt):
        """
        Convert a Matplotlib plot to a Base64-encoded string.

        This function converts a Matplotlib plot to a Base64-encoded string
        so that it can be embedded in web pages or other documents.

        Args:
            plt (matplotlib.pyplot): The Matplotlib plot to convert.

        Returns:
            str: A Base64-encoded string representation of the plot.
        """
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_data = buffer.getvalue()
        buffer.close()
        return base64.b64encode(plot_data).decode('utf-8')

    @classmethod
    def generate_plots(cls, selected_assets, mark_output, nazwa_portfela):
        """
        Generate and save plots for selected assets.

        This function generates line charts and a pie chart based on selected assets
        and their weights. It also saves the generated charts to the project directory.

        Args:
            selected_assets (list): A list of selected asset names.
            mark_output (dict): A dictionary containing asset weights.

        Returns:
            list: A list of portfolio values over time.
        """
        # Line chart of asset values over time
        plt.figure(figsize=(12, 6))
        mp = DataFunctions.prepare_data(selected_assets).set_index("Month")
        mp = mp.sort_values(by="Month")
        for asset_name in selected_assets:
            plt.plot(mp.index, mp[asset_name], label=asset_name)
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.title('Asset Values Over Time')
        plt.legend()
        plt.grid(True)

        # Rotate X-axis labels by 90 degrees
        plt.xticks(rotation=90)

        # Save the chart to the project directory
        plot1_path = os.path.join(PROJECT_DIR, 'staticfiles', f'{nazwa_portfela}1.png')
        plt.savefig(plot1_path, format='png')

        # Line chart of portfolio values over time
        portfolio_values = DataFunctions.calculate_portfolio_values(selected_assets, mark_output)
        plt.figure(figsize=(12, 6))
        plt.plot(mp.index, portfolio_values, label='Portfolio')
        plt.xlabel('Time')
        plt.ylabel('Portfolio Value')
        plt.title('Portfolio Value Over Time')
        plt.grid(True)

        # Rotate X-axis labels by 90 degrees
        plt.xticks(rotation=90)

        # Save the chart to the project directory
        plot2_path = os.path.join(PROJECT_DIR, 'staticfiles', f'{nazwa_portfela}2.png')
        plt.savefig(plot2_path, format='png')

        # Pie chart with asset weights
        weights = [mark_output[asset_name] for asset_name in selected_assets]
        plt.figure(figsize=(6, 6))
        plt.pie(weights, labels=selected_assets, autopct='%1.1f%%', startangle=140)
        plt.title('Asset Weights in Portfolio')

        # Save the chart to the project directory
        plot3_path = os.path.join(PROJECT_DIR, 'staticfiles', f'{nazwa_portfela}3.png')
        plt.savefig(plot3_path, format='png')

        portfolio_values = portfolio_values.tolist()
        return portfolio_values

    @classmethod
    def maximum_drawdown(cls, profit_data):
        """
        Calculate the maximum drawdown of a profit curve.

        This function calculates the maximum drawdown of a profit curve, which
        represents the largest loss from a peak to a trough in the portfolio's value.

        Args:
            profit_data (list): A list of portfolio values over time.

        Returns:
            float: The maximum drawdown as a percentage.
        """
        max_drawdown = 0.0
        peak = profit_data[0]  # First/ start point

        for value in profit_data:
            if value > peak:
                peak = value
            else:
                drawdown = (peak - value) / peak
                max_drawdown = builtins.max(max_drawdown, drawdown)

        return round(max_drawdown * 100)