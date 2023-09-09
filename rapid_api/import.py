import requests
import pandas as pd

url = "https://alpha-vantage.p.rapidapi.com/query"

querystring = {"symbol":"BCX","function":"TIME_SERIES_INTRADAY","interval":"60min","output_size":"compact","datatype":"json"}

headers = {
	"X-RapidAPI-Key": "da0b3caac4msh109d28e7cce8bb4p150d6bjsn6fba862d7c27",
	"X-RapidAPI-Host": "alpha-vantage.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

df = pd.DataFrame(response.json()["Time Series (60min)"]).transpose()

print(df)