import threading
from symbol_scanner import scan_symbols
from logic_engine import decide_trade
from trade_executor import execute_trade
from sentiment_analyzer import update_sentiment
from ai_brain import learn_from_trade
import web_interface
import time

def run_bot():
    print("🚀 ULTIMATE_AI_TRADER (REAL) стартира...")
    while True:
        symbols = scan_symbols()

        for symbol in symbols:
            sentiment_score = update_sentiment(symbol)
            decision = decide_trade(symbol, sentiment_score)

            if decision['action'] != 'HOLD':
                result = execute_trade(symbol, decision['action'], 5)
                learn_from_trade(symbol, decision, result)

            time.sleep(1)
        time.sleep(10)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=lambda: web_interface.app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False))
    flask_thread.daemon = True
    flask_thread.start()

    run_bot()
