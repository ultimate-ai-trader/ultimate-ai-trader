
def learn_from_trade(symbol, decision, result):
    with open("logs/trades.log", "a") as f:
        f.write(f"{symbol} | {decision['action']} | Result: {str(result)}\n")
