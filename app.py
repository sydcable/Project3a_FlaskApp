import pygal
import requests
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, url_for, flash, redirect, abort

# make a Flask application object called app
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your seceret key'

def get_stock_symbols(csv_path = 'stocks.csv'): 
    try:
        df = pd.read_csv('stocks.csv') 
        if "Symbol" in df.columns:
            return [str(s).strip() for s in df["Symbol"].dropna().unique()]
        else:
            return []
    except Exception:
        return[]

def filter_data(time_series, start_date, end_date):
    filtered = {}
    for date_str, values in time_series.items():
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue

        if not (start_date <= date <= end_date):
            continue
        try:
            open_val = float(values.get("1. open") or values.get("open"))
            high_val = float(values.get("2. high") or values.get("high"))
            low_val = float(values.get("3. low") or values.get("low"))
            close_val = float(values.get("4. close") or values.get("close"))
        except Exception:
            continue

        filtered[date] = {
            "open": open_val,
            "high": high_val,
            "low": low_val,
            "close": close_val
        }

    return dict(sorted(filtered.items()))

def plot_data(data, symbol, chart_type):
    if not data:
        return None
    
    sorted_dates = sorted(data.keys())

    open_data = [data[d]["open"] for d in sorted_dates]
    high_data = [data[d]["high"] for d in sorted_dates]
    low_data  = [data[d]["low"] for d in sorted_dates]
    close_data = [data[d]["close"] for d in sorted_dates]

    # Convert dates to strings for Pygal
    x_labels = [d.strftime("%Y-%m-%d") for d in sorted_dates]

    if chart_type == 'Line':
        chart = pygal.Line()
        chart.title = f"{symbol} Stock Prices (OHLC)"
        chart.x_labels = x_labels
        chart.add("Open", open_data)
        chart.add("High", high_data)
        chart.add("Low", low_data)
        chart.add("Close", close_data)
        return chart
    elif chart_type == 'Bar':
        chart = pygal.Bar()
        chart.title = f"{symbol} Stock Prices (OHLC)"
        chart.x_labels = x_labels
        chart.add("Open", open_data)
        chart.add("High", high_data)
        chart.add("Low", low_data)
        chart.add("Close", close_data)
        return chart


@app.route('/', methods=('GET', 'POST'))
def index():
    
    stocks = get_stock_symbols()
    chart= None
    selected_symbol = None
    chart_type = None
    time_series = None
    start_input = None
    end_input = None
    

    # API and Time Series Function
    if request.method == 'POST':
        selected_symbol = request.form.get('symbol')
        chart_type=request.form.get('chart')
        time_series = request.form.get('time_series')
        start_input = request.form.get('start_input')
        end_input = request.form.get('end_input')

        if not selected_symbol:
            flash("Stock selection required")
            return render_template('index.html', stocks=stocks, chart=None)

        if not chart_type:
            flash("Chart type required")
            return render_template('index.html', stocks=stocks, chart=None)

        if not time_series:
            flash("Time series required")
            return render_template('index.html', stocks=stocks, chart=None)
        
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
        

        if not start_input or not end_input:
            flash("Start and end date required")
            return render_template('index.html', stocks=stocks, chart=None)

        try:
            start_date = datetime.strptime(start_input, "%Y-%m-%d")
            end_date = datetime.strptime(end_input, "%Y-%m-%d")
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.")
            return render_template("index.html", stocks=stocks, chart=None)

        if end_date < start_date:
            flash("End date cannot be before start date.")
            return redirect(url_for('index', stocks=stocks, chart=None))
            
        r = requests.get(url)
        data = r.json()

        if "Error Message" in data:
            flash("Invalid stock symbol.")
            return redirect(url_for("index"))

        if "Note" in data:
            flash("API rate limit reached. Wait 1 minute.")
            return redirect(url_for("index"))

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
        
        chart_svg = chart.render_data_uri()
        return render_template("index.html", stocks=stocks, chart=chart_svg, selected_symbol=selected_symbol, chart_type=chart_type, time_series=time_series, start_date=start_date, end_date=end_date)

    return render_template('index.html', stocks=stocks, chart=None)

app.run(host="0.0.0.0")