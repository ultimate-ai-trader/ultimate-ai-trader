
import pandas as pd
import numpy as np
import yfinance as yf
import ta

last_signal = {}

def get_last_signal():
    return last_signal

def decide_trade(symbol, sentiment_score):
    global last_signal
    try:
        yahoo_map = {
            "tLTCUSD": "LTC-USD",
            "tBTCUSD": "BTC-USD",
            "tETHUSD": "ETH-USD",
            "tXRPUSD": "XRP-USD"
        }

        yahoo_symbol = yahoo_map.get(symbol)
        if not yahoo_symbol:
            return {"action": "HOLD", "reason": "symbol not supported"}

        data = yf.download(yahoo_symbol, period="2d", interval="15m", progress=False)
        if data.empty or len(data) < 30:
            return {"action": "HOLD", "reason": "not enough data"}

        df = data.copy()
        df.dropna(inplace=True)

        df["rsi"] = ta.momentum.RSIIndicator(df["Close"], window=14).rsi()
        macd = ta.trend.MACD(df["Close"])
        df["macd"] = macd.macd()
        df["macd_signal"] = macd.macd_signal()
        df["ema9"] = ta.trend.EMAIndicator(df["Close"], window=9).ema_indicator()
        df["ema21"] = ta.trend.EMAIndicator(df["Close"], window=21).ema_indicator()
        bb = ta.volatility.BollingerBands(df["Close"])
        df["bb_upper"] = bb.bollinger_hband()
        df["bb_lower"] = bb.bollinger_lband()

        last = df.iloc[-1]

        buy_signals = 0
        sell_signals = 0

        if last["rsi"] < 30: buy_signals += 1
        elif last["rsi"] > 70: sell_signals += 1

        if last["macd"] > last["macd_signal"]: buy_signals += 1
        elif last["macd"] < last["macd_signal"]: sell_signals += 1

        if last["ema9"] > last["ema21"]: buy_signals += 1
        elif last["ema9"] < last["ema21"]: sell_signals += 1

        if last["Close"] < last["bb_lower"]: buy_signals += 1
        elif last["Close"] > last["bb_upper"]: sell_signals += 1

        if sentiment_score > 0.5: buy_signals += 1
        elif sentiment_score < -0.5: sell_signals += 1

        action = "HOLD"
        if buy_signals >= 3:
            action = "BUY"
        elif sell_signals >= 3:
            action = "SELL"

        signal = {
            "symbol": symbol,
            "action": action,
            "buy_signals": buy_signals,
            "sell_signals": sell_signals,
            "rsi": last["rsi"],
            "macd": last["macd"],
            "macd_signal": last["macd_signal"],
            "ema9": last["ema9"],
            "ema21": last["ema21"],
            "close": last["Close"]
        }

        last_signal = signal
        return {"action": action, "details": signal}

    except Exception as e:
        return {"action": "HOLD", "reason": str(e)}
