import streamlit as st
import requests

st.set_page_config(page_title="Krypto Çmimet Live", page_icon="📈", layout="centered")

st.title("📊 Krypto Çmimet Live nga CoinGecko")
st.write("Ky dashboard tregon çmimet aktuale për Bitcoin, Dogecoin dhe XRP.")

# Lista e monedhave që duam të shfaqim
coins = {
    "Bitcoin (BTC)": "bitcoin",
    "Dogecoin (DOGE)": "dogecoin",
    "XRP (Ripple)": "ripple"
}

vs_currency = "usd"
url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(coins.values())}&vs_currencies={vs_currency}"

try:
    response = requests.get(url)
    data = response.json()

    st.subheader("💰 Çmimet aktuale (USD):")
    for name, api_id in coins.items():
        price = data.get(api_id, {}).get(vs_currency)
        if price is not None:
            st.metric(label=name, value=f"${price:,.4f}")
        else:
            st.warning(f"Nuk u morën të dhëna për {name}")

except Exception as e:
    st.error("❌ Gabim gjatë marrjes së të dhënave. Kontrollo lidhjen me internetin ose CoinGecko API.")
    st.code(str(e), language="python")

st.markdown("---")
st.caption("Powered by CoinGecko API • Streamlit App nga Buniarena")
