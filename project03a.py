import requests
import matplotlib.pyplot as plt
import sys
from datetime import datetime
from flask import Flask, render_template, request, url_for, flash, redirect, abort

# make a Flask application object called app
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your seceret key'

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
    plt.save()


@app.route('/', methods=('GET', 'POST'))
def index():
    
    selected_symbol = request.form['symbol']
    chart_
    

    # API and Time Series Function
    def get_api_data(symbol, function):
    if function == "Intradaily":
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey=2O7W9WY18QMH3DXR"
    elif function == "Daily":
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey=2O7W9WY18QMH3DXR"
    elif function == "Weekly":
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={symbol}&apikey=2O7W9WY18QMH3DXR"
    elif function == "Monthly":
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={symbol}&apikey=2O7W9WY18QMH3DXR"
    
    response = requests.get(url)
    data = response.json()
    return data

    start_date = datetime.strptime(start_input, "%Y-%m-%d")
    end_date = datetime.strptime(end_input, "%Y-%m-%d")
    if end_date < start_date:
        alert("End date cannot be before start date.")
            
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
        

    # Fetch and process data
    data = get_api_data(symbol, function)
    time_series = extract_time_series(data)
    if not time_series:
        print("Could not retrieve time series data. Check symbol.")
        return

    filtered_data = filter_data(time_series, start_date, end_date)
    if not filtered_data:
        print("No data available for the selected date range.")
        return

    plot_data(filtered_data, symbol, chart_type)

    # Ask to continue or exit
    if not ask_yes_no("Would you like to view more stock data? (y/n): "):
        print("Exiting program.")
        sys.exit(0)

    return render_template('index.html', symbol=symbol)
