import requests
import matplotlib.pyplot as plt
import sys
from datetime import datetime

def get_api_data(symbol, function):
    api_key = "2O7W9WY18QMH3DXR"
    if function == "TIME_SERIES_INTRADAY":
        interval = "5min"
        url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&interval={interval}&apikey={api_key}"
    else:
        url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={api_key}"
    
    response = requests.get(url)
    data = response.json()
    return data

def get_time_series_function(choice):
    functions = {
        "1": "TIME_SERIES_INTRADAY",
        "2": "TIME_SERIES_DAILY",
        "3": "TIME_SERIES_WEEKLY",
        "4": "TIME_SERIES_MONTHLY"
    }
    return functions.get(choice, None)

def get_chart_type(choice):
    chart_types = {
        "1": "bar",
        "2": "line"
    }
    return chart_types.get(choice, None)

def extract_time_series(data):
    for key in data.keys():
        if "Time Series" in key:
            return data[key]
    return None

def filter_data(time_series, start_date, end_date):
    filtered = {}
    for date_str, values in time_series.items():
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        if start_date <= date <= end_date:
            filtered[date] = float(values["4. close"])
    return dict(sorted(filtered.items()))

def plot_data (data, symbol, chart_type):
    dates = list (data.keys())
    prices = list (data.values())

    plt.figure(figsize=(10,5))
    if chart_type == "bar":
        plt.bar(dates, prices, color='skyblue')
    else:
        plt.plot(dates, prices, color='orange')

    plt.title(f"{symbol} Stock Prices")
    plt.xlabel("Date")
    plt.ylabel("Closing Price (USD)")
    plt.tight_layout()
    plt.show()

def ask_yes_no(prompt: str) -> bool:
    """Return True for yes, False for no."""
    while True:
        ans = input(prompt).strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("Please enter y or n.")

def main():
    while True:
        print("Stock Data Visualizer\n----------------------")

        # stock symbol
        symbol = input("Enter the stock symbol (e.g., IBM, AAPL, TSLA): ").upper()

        # chart type
        print("\nChart Types:\n--------------\n1. Bar\n2. Line")
        chart_choice = input("Enter the chart type you want (1 or 2): ")
        chart_type = get_chart_type(chart_choice)
        if not chart_type:
            print("Invalid chart type selected. Enter 1 or 2.")
            continue

        # time series function
        print("\nSelect the Time Series of the chart you want to generate:\n-----------------------------------")
        print("1. Intradaily\n2. Daily\n3. Weekly\n4. Monthly")
        time_choice = input("Enter the time series option (1-4): ")
        function = get_time_series_function(time_choice)
        if not function:
            print("Invalid time series option.")
            continue

        # date range
        start_input = input("\nEnter the start date (YYYY-MM-DD): ")
        end_input = input("Enter the end date (YYYY-MM-DD): ")

        try:
            start_date = datetime.strptime(start_input, "%Y-%m-%d")
            end_date = datetime.strptime(end_input, "%Y-%m-%d")
            if end_date < start_date:
                print("End date cannot be before start date.")
                continue
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")
            continue

        # Fetch and process data
        data = get_api_data(symbol, function)
        time_series = extract_time_series(data)
        if not time_series:
            print("Could not retrieve time series data. Check symbol.")
            continue

        filtered_data = filter_data(time_series, start_date, end_date)
        if not filtered_data:
            print("No data available for the selected date range.")
            continue

        plot_data(filtered_data, symbol, chart_type)

        # Ask to continue or exit
        if not ask_yes_no("Would you like to view more stock data? (y/n): "):
            print("Exiting program.")
            sys.exit(0)

if __name__ == "__main__":
    main()