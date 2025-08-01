
from flask import Flask, render_template_string
from logic_engine import get_last_signal
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd
import os
import time
import hmac
import hashlib
import json
import requests
from config import API_KEY, API_SECRET

app = Flask(__name__)

def read_trade_log():
    log_file = "logs/trades.log"
    if not os.path.exists(log_file):
        return []
    with open(log_file, "r") as f:
        lines = f.readlines()[-10:]
        return [line.strip() for line in lines if line.strip()]

def get_price_chart(symbol):
    yahoo_map = {
        "tLTCUSD": "LTC-USD",
        "tBTCUSD": "BTC-USD",
        "tETHUSD": "ETH-USD",
        "tXRPUSD": "XRP-USD"
    }
    yf_symbol = yahoo_map.get(symbol, "BTC-USD")
    df = yf.download(yf_symbol, period="2d", interval="15m", progress=False)

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price'))

    fig.update_layout(
        title=f'📈 {yf_symbol} (15m candles)',
        xaxis_title='Time',
        yaxis_title='Price (USD)',
        template='plotly_dark',
        height=500
    )
    return fig.to_html(full_html=False)

def get_bitfinex_balances():
    url = "https://api.bitfinex.com/v2/auth/r/wallets"
    nonce = str(int(time.time() * 1000000))
    body = {}
    raw_body = json.dumps(body)
    signature_payload = f"/api/v2/auth/r/wallets{nonce}{raw_body}".encode()
    signature = hmac.new(API_SECRET.encode(), signature_payload, hashlib.sha384).hexdigest()

    headers = {
        "bfx-nonce": nonce,
        "bfx-apikey": API_KEY,
        "bfx-signature": signature,
        "content-type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, data=raw_body)
        wallets = response.json()
        balances = {}
        for wallet in wallets:
            currency = wallet[1]
            balance = float(wallet[2])
            if balance > 0:
                balances[currency] = balance
        return balances
    except Exception as e:
        return {"error": str(e)}

@app.route("/")
def index():
    signal = get_last_signal()
    trade_log = read_trade_log()
    chart_html = get_price_chart(signal["symbol"]) if signal else "<p>Няма налични данни.</p>"
    balances = get_bitfinex_balances()
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ultimate AI Trader - Full Dashboard</title>
        <style>
            body { font-family: Arial; padding: 20px; background: #101010; color: #eee; }
            h1 { color: #0af; }
            .box { background: #1a1a1a; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 0 10px #222; }
            .trade-log { font-family: monospace; background: #222; padding: 10px; border-radius: 6px; }
            .chart { background: #111; padding: 10px; border-radius: 10px; }
        </style>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    </head>
    <body>
        <h1>🚀 Ultimate AI Trader — FULL Dashboard</h1>

        <div class="box">
            <h2>📊 Последен сигнал</h2>
            {% if signal %}
                <p>Символ: <b>{{ signal.symbol }}</b></p>
                <p>Действие: <b>{{ signal.action }}</b></p>
                <p>Цена: {{ signal.close }} USD</p>
                <p>RSI: {{ signal.rsi }}</p>
                <p>MACD: {{ signal.macd }} / {{ signal.macd_signal }}</p>
                <p>EMA: {{ signal.ema9 }} / {{ signal.ema21 }}</p>
                <p>BUY сигнали: {{ signal.buy_signals }} / SELL сигнали: {{ signal.sell_signals }}</p>
            {% else %}
                <p>Няма активен сигнал.</p>
            {% endif %}
        </div>

        <div class="box chart">
            {{ chart_html|safe }}
        </div>

        <div class="box">
            <h2>📈 Последни сделки</h2>
            <div class="trade-log">
                {% for trade in trade_log %}
                    {{ trade }}<br>
                {% else %}
                    Няма записани сделки още.
                {% endfor %}
            </div>
        </div>

        <div class="box">
            <h2>💰 Баланси по валути</h2>
            {% if balances.get('error') %}
                <p>Грешка при извличане на баланс: {{ balances.error }}</p>
            {% else %}
                {% for coin, value in balances.items() %}
                    <p>{{ coin }}: {{ value }}</p>
                {% endfor %}
            {% endif %}
        </div>
    </body>
    </html>
    """, signal=signal, trade_log=trade_log, chart_html=chart_html, balances=balances)

if __name__ == "__main__":
    app.run(debug=False)
