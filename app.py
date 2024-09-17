from flask import Flask, render_template, request, url_for, flash, redirect
import pandas as pd
import yfinance as yf
import riskfolio as rp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'e6f469c376e0724c6cc76a694549c290b02ff4ba56f727c0'

messages = {}
stocks = list()

@app.route("/old", methods=('GET', 'POST'))
def main():
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']

        if not name:
            flash('name is required!')
        elif not quantity:
            flash('Quantity is required!')
        else:
            messages[name] = quantity
            return redirect(url_for('main'))

    length = len(messages)

    beta = 0

    if len(messages) == 0:
        beta = 0
    
    elif len(messages) == 1:
        key = list(messages.keys())[0]
        beta = yf.Ticker(key+".ns").info['beta']
    
    else:
        total_weight = 0
        for key, value in messages.items():
            total_weight += yf.Ticker(key+".ns").info['currentPrice'] * int(value)
        
        for key,value in messages.items():
            weight = yf.Ticker(key+".ns").info['currentPrice'] * int(value) / total_weight
            beta += yf.Ticker(key+".ns").info['beta'] * weight
    
    return render_template('base.html', messages=messages, length = length,beta=beta)


@app.route('/', methods=["GET"])
@app.route('/home', methods = ["GET", "POST"])
def home():
    return render_template('home.html')
      
@app.route('/portfolio', methods=["GET", "POST"])
def create():
    data = {}
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        price = request.form['price']
        date = request.form['date']

        if not name:
            flash('name is required!')
        elif not quantity:
            flash('Quantity is required!')
        elif not price:
            flash('Price is required!')
        else:
            data['name']=name
            data['qty']=quantity
            data['price']=price
            data['date']=date
            stocks.append(data)   
            return redirect(url_for('portfolio'))     
    
    if len(stocks) > 1:
        df = pd.DataFrame(stocks)
        df_html = df.to_html(header=True, index=False)
        
        names=df['name'].tolist()

        # Date range
        start = '2020-01-01'
        end = '2024-07-31'

        # Tickers of assets
        tickers = []
        for sec in names:
            sec = sec + ".ns"
            tickers.append(sec)
        tickers.sort()

        # Downloading the data
        data = yf.download(tickers, start = start, end = end)
        data = data.loc[:,('Adj Close', slice(None))]
        data.columns = tickers
        assets = data.pct_change().dropna()

        Y = assets

        # Creating the Portfolio Object
        port = rp.Portfolio(returns=Y)

        # To display dataframes values in percentage format
        pd.options.display.float_format = '{:.4%}'.format

        # Choose the risk measure
        rm = 'MV'  # Standard Deviation

        # Estimate inputs of the model (historical estimates)
        method_mu='hist' # Method to estimate expected returns based on historical data.
        method_cov='hist' # Method to estimate covariance matrix based on historical data.

        port.assets_stats(method_mu=method_mu, method_cov=method_cov)

        # Estimate the portfolio that maximizes the risk adjusted return ratio
        w = port.optimization(model='Classic', rm=rm, obj='Sharpe', rf=0.0, l=0, hist=True)
        print(w)
        return render_template('portfolio.html', stocks=stocks, tables = w)  
    else:
        return render_template('portfolio.html',stocks=stocks)

@app.route('/contact', methods=["GET", "POST"])
def portfolio():
    return render_template('contact.html')

