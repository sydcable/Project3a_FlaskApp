import requests
import matplotlib.pyplot as plt
import sys
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, url_for, flash, redirect, abort

# make a Flask application object called app
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your seceret key'

def get_stock_symbols(): 
    df = pd.read_csv('stocks.csv') 
    return df['Symbol'].tolist()


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
    
    stocks = get_stock_symbols()
    selected_symbol = None
    chart_type = None
    plot_data = None
    time_series = None
    start_input = None
    end_input = None
    

    # API and Time Series Function
    if request.method == 'POST':
        selected_symbol = request.form['symbol']
        if not selected_symbol:
            flash("Stock selection required")
        chart_type=request.form['chart']
        if not chart_type:
            flash("Chart type required")
        time_series = request.form['time_series']
        if not time_series:
            flash("Time series required")
        
        if time_series == "Intraday":
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey=2O7W9WY18QMH3DXR"
        elif time_series == "Daily":
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey=2O7W9WY18QMH3DXR"
        elif time_series == "Weekly":
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={symbol}&apikey=2O7W9WY18QMH3DXR"
        elif time_series == "Monthly":
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={symbol}&apikey=2O7W9WY18QMH3DXR"
        
    start_input = request.form['start_input']
    if not start_input:
        flash("Start date required")
    start_date = datetime.strptime(start_input, "%Y-%m-%d")
    end_input = request.form['end_input']
    if not end_input:
        flash("End date required")
    end_date = datetime.strptime(start_input, "%Y-%m-%d")
    if end_date < start_date:
        flash("End date cannot be before start date.")
        return redirect(url_for('index'))
            
    r = requests.get(url)
    data = r.json()
        

    # Fetch and process data
    data = get_api_data(symbol, function)
    time_series = extract_time_series(data)
    if not time_series:
        flash("Could not retrieve time series data. Check symbol.")
        return

    filtered_data = filter_data(time_series, start_date, end_date)
    if not filtered_data:
        flash("No data available for the selected date range.")
        return

    plot_data(filtered_data, symbol, chart_type)

    return render_template('index.html', symbol=selected_symbol, )
