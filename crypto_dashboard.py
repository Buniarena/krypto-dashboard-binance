def fetch_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "1", "interval": "minutely"}
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            prices = data["prices"]
            df = pd.DataFrame(prices, columns=["timestamp", "price"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)

            now = datetime.utcnow()
            two_hours_ago = now - timedelta(hours=2)
            df = df[df.index >= two_hours_ago]
            return df
        else:
            st.warning(f"⛔ Gabim {response.status_code} nga CoinGecko")
            return None
    except Exception as e:
        st.error(f"❌ Gabim: {e}")
        return None
