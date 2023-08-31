import pandas as pd

# Lista nazw aktywów
tickers = ["cdr", "abe", "bcx"]  # Dodaj tutaj nazwy aktywów

# Tworzenie listy nazw plików na podstawie nazw aktywów
file_names = [f"data/{ticker}.txt" for ticker in tickers]

# Inicjalizacja pustego DataFrame
df = pd.DataFrame(columns=["Ticker", "Date"])

# Ładowanie danych z plików i dodawanie kolumn "Close" dla różnych aktywów
for file_name, ticker in zip(file_names, tickers):
    data = []
    with open(file_name, "r") as file:
        lines = file.readlines()
        for line in lines[1:]:
            parts = line.strip().split(",")
            _, _, date, _, _, _, _, close, _, _ = parts
            data.append((ticker, date, float(close)))
    
    df_ticker = pd.DataFrame(data, columns=["Ticker", "Date", f"{ticker}_Close"])
    df_ticker["Date"] = pd.to_datetime(df_ticker["Date"], format="%Y%m%d")
    df = pd.merge(df, df_ticker, on=["Ticker", "Date"], how="outer")

# Dodawanie kolumny "Month" z formatem roku i miesiąca
df["Month"] = df["Date"].dt.to_period("M")

# Grupowanie po miesiącu i obliczanie średniej dla kolumn "Close" dla różnych aktywów
columns_to_group = [f"{ticker}_Close" for ticker in tickers]
columns_to_group.insert(0, "Month")
monthly_average = df.groupby("Month")[columns_to_group].mean().reset_index()

print(monthly_average)