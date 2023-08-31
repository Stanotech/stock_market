import pandas as pd

# Lista nazw aktywów
tickers = ["cdr", "tim", "pko"]  # Dodaj tutaj nazwy aktywów

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
    
    df_ticker = pd.DataFrame(data, columns=["Ticker", "Date", f"{ticker}"])
    df_ticker["Date"] = pd.to_datetime(df_ticker["Date"], format="%Y%m%d")
    df = pd.merge(df, df_ticker, on=["Ticker", "Date"], how="outer")

# Dodawanie kolumny "Month" z formatem roku i miesiąca
df["Month"] = df["Date"].dt.to_period("M")

# Lista kolumn do grupowania, bez kolumny "Month"
columns_to_group = [f"{ticker}" for ticker in tickers]
monthly_average = df.groupby("Month")[columns_to_group].mean().reset_index()

# Usuwanie wierszy z miesiącami, w których nie wszystkie aktywa mają wartości
all_tickers_columns = set(df.columns)
missing_data_months = monthly_average[monthly_average[columns_to_group].isnull().any(axis=1)]["Month"]
valid_months = monthly_average[~monthly_average["Month"].isin(missing_data_months)]
if valid_months.empty:
    print("Aktywa nie współistnieją.")
else:
    print(valid_months)