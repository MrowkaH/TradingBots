import ccxt
import time

exchange = ccxt.mexc({
    'apiKey': 'YOUR_API_KEY',
    'secret': 'YOUR_SECRET_KEY',
})

FIB_LEVELS = [0.5, 0.618, 0.786, 0.886, 0.927]

def get_historical_data(symbol, limit=100):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe='15m', limit=limit)
    return ohlcv

def calculate_fib_levels(high, low):
    diff = high - low
    return {level: low + diff * level for level in FIB_LEVELS}

def check_fib_intersection(current_price, fib_levels):
    for level, price in fib_levels.items():
        if abs(current_price - price) < 0.1:  # Tolerancja 0.1
            return level, price
    return None, None

def main():
    symbol = 'US500/USD'
    while True:
        try:
            ohlcv = get_historical_data(symbol)
            closes = [x[4] for x in ohlcv]
            highs = [x[2] for x in ohlcv]
            lows = [x[3] for x in ohlcv]

            swing_high = max(highs)
            swing_low = min(lows)

            fib_levels = calculate_fib_levels(swing_high, swing_low)

            ticker = exchange.fetch_ticker(symbol)
            current_price = ticker['last']

            level, price = check_fib_intersection(current_price, fib_levels)
            if level is not None:
                print(f"Cena przecina poziom Fibonacciego {level * 100}%: {price}")
            else:
                print("Brak przecięcia z poziomami Fibonacciego.")

            time.sleep(900)  # 15 minut

        except Exception as e:
            print("Wystąpił błąd:", e)
            time.sleep(10)

if __name__ == "__main__":
    main()