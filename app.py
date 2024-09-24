from flask import Flask, render_template, request, url_for, flash, redirect
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "e6f469c376e0724c6cc76a694549c290b02ff4ba56f727c0"

messages = {}
stocks = list()


@app.route("/old", methods=("GET", "POST"))
def main():
    if request.method == "POST":
        name = request.form["name"]
        quantity = request.form["quantity"]

        if not name:
            flash("name is required!")
        elif not quantity:
            flash("Quantity is required!")
        else:
            messages[name] = quantity
            return redirect(url_for("main"))

    length = len(messages)

    beta = 0

    if len(messages) == 0:
        beta = 0

    elif len(messages) == 1:
        key = list(messages.keys())[0]
        beta = yf.Ticker(key + ".ns").info["beta"]

    else:
        total_weight = 0
        for key, value in messages.items():
            total_weight += yf.Ticker(key + ".ns").info["currentPrice"] * int(value)

        for key, value in messages.items():
            weight = (
                yf.Ticker(key + ".ns").info["currentPrice"] * int(value) / total_weight
            )
            beta += yf.Ticker(key + ".ns").info["beta"] * weight

    return render_template("base.html", messages=messages, length=length, beta=beta)


@app.route("/", methods=["GET"])
@app.route("/home", methods=["GET", "POST"])
def home():
    return render_template("home.html")


@app.route("/portfolio", methods=["GET", "POST"])
def portfolio():
    data = {}

    if request.method == "POST":
        name = request.form["name"]
        quantity = request.form["quantity"]
        price = request.form["price"]
        date = request.form["date"]

        if not name:
            flash("name is required!")
        elif not quantity:
            flash("Quantity is required!")
        elif not price:
            flash("Price is required!")
        else:
            data["name"] = name
            data["qty"] = quantity
            data["price"] = price
            data["date"] = date
            stocks.append(data)
            leng = len(stocks)
            print(leng)
            return redirect(url_for("portfolio"))
    
    df = pd.DataFrame(stocks)
    
    
    #Taking the stocks list from total data
    stocks_list = []
    total_value=0
    weights = {}

    if df.empty:
        pass
    else:
        df.qty = df.qty.astype("int32")
        df.price = df.price.astype("int32")
        stocks_list = df['name'].tolist()
        df["value"] = df["qty"] * df["price"]
        total_value = df["value"].sum()
        
    num_of_stocks = len(stocks_list)
    
    if num_of_stocks>0:
        for st in stocks_list:
            weights[st] = round(float((df.set_index('name').loc[st,"price"] * \
                 df.set_index('name').loc[st,"qty"])/total_value),2)

    
    return render_template("portfolio.html", tables=df.to_html(index=False), \
                            num_of_stocks=num_of_stocks, \
                            total_value=total_value, \
                            weights = weights)


@app.route("/about", methods=["GET", "POST"])
def about():
    return render_template("about.html")
