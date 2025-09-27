# services/market_service.py

import requests
import yfinance as yf

def get_top_crypto_prices():
    try:
        return requests.get(
            "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1",
            timeout=10).json()
    except Exception:
        return []

def get_prices_for_portfolio(coin_ids):
    try:
        ids_string = ",".join(coin_ids)
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_string}&vs_currencies=usd"
        return requests.get(url, timeout=10).json()
    except Exception:
        return {}

def get_market_data(tickers):
    data_list = []
    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info
            current_price = info.get('currentPrice', 0)
            previous_close = info.get('previousClose', 1)
            change_percent = ((current_price - previous_close) / previous_close) * 100 if previous_close else 0
            data_list.append({
                'symbol': ticker,
                'price': current_price,
                'name': info.get('shortName', ticker),
                'change_percent': change_percent
            })
        except Exception:
            continue
    return data_list