import requests
import matplotlib 
matplotlib.use('Agg')
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
    stocks = []
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

def plot_data(data, symbol, chart_type):
    dates = list(data.keys())
    prices = list(data.values())

    plt.figure(figsize=(10, 5))
    
    if chart_type == "bar":
        plt.bar(dates, prices)
    else:
        plt.plot(dates, prices)
    
    plt.title(f"{symbol} Stock Prices")
    plt.xlabel("Date")
    plt.ylabel("Closing Price (USD)")
    plt.tight_layout()

    filename = f"static/{symbol}_chart.png"
    plt.savefig(filename)
    plt.close() 

    return filename

@app.route('/', methods=('GET', 'POST'))
def index():
    
    stocks = get_stock_symbols()
    selected_symbol = None
    chart_type = None
    ##plot_data = None
    time_series = None
    start_input = None
    end_input = None
    

    # API and Time Series Function
    if request.method == 'POST':
        selected_symbol = request.form.get('symbol')
        if not selected_symbol:
            flash("Stock selection required")
        chart_type=request.form.get('chart')
        if not chart_type:
            flash("Chart type required")
        time_series = request.form.get('time_series')
        if not time_series:
            flash("Time series required")
        
        if time_series == "Intraday":
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={selected_symbol}&interval=5min&apikey=2O7W9WY18QMH3DXR"
            ts_key= "Time Series (5min)"
        elif time_series == "Daily":
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={selected_symbol}&apikey=2O7W9WY18QMH3DXR"
            ts_key= "Time Series (Daily)"
        elif time_series == "Weekly":
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={selected_symbol}&apikey=2O7W9WY18QMH3DXR"
            ts_key= "Weekly Time Series"
        elif time_series == "Monthly":
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={selected_symbol}&apikey=2O7W9WY18QMH3DXR"
            ts_key= "Monthly Time Series"
        
        start_input = request.form.get('start_input')
        end_input = request.form.get('end_input')
        if not start_input or not end_input:
            flash("Start and end date required")

        start_date = datetime.strptime(start_input, "%Y-%m-%d")
        end_date = datetime.strptime(end_input, "%Y-%m-%d")
        if end_date < start_date:
            flash("End date cannot be before start date.")
            return redirect(url_for('index'))
            
        r = requests.get(url)
        data = r.json()

        if ts_key not in data:
            flash("API returned no time series data.")
            return redirect(url_for("index"))

        filtered = filter_data(data[ts_key], start_date, end_date)
        if not filtered:
            flash("No data in selected date range.")
            return redirect(url_for("index"))

        # Generate chart
        chart = plot_data(filtered, selected_symbol, chart_type)
        if not chart:
            flash("No valid time series data found.")
            return redirect('index')
        
        return render_template('index.html', stocks=stocks, chart=chart)

    return render_template('index.html', stocks=stocks, chart=None)

app.run(port=5008)