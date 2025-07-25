def fetch_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "1", "interval": "minute"}
    headers = {
        "User-Agent": "MyCryptoDashboard/1.0"
    }
    r = requests.get(url, params=params, headers=headers)
    r.raise_for_status()
    prices = r.json()["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df
