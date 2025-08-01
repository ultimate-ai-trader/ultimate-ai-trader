
import time
import hmac
import hashlib
import json
import requests
from config import API_KEY, API_SECRET

def execute_trade(symbol, side, usd_amount):
    url_path = "/v2/auth/w/order/submit"
    url = "https://api.bitfinex.com" + url_path

    nonce = str(int(time.time() * 1000000))
    amount = str(usd_amount if side == "BUY" else -usd_amount)

    body = {
        "type": "MARKET",
        "symbol": symbol,
        "amount": amount
    }

    raw_body = json.dumps(body)
    signature_payload = f"/api{url_path}{nonce}{raw_body}".encode()
    signature = hmac.new(API_SECRET.encode(), signature_payload, hashlib.sha384).hexdigest()

    headers = {
        "bfx-nonce": nonce,
        "bfx-apikey": API_KEY,
        "bfx-signature": signature,
        "content-type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, data=raw_body)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
