import streamlit as st
import requests

st.title("Çmimet Live: Nafta dhe Ari")

# Vendos këtu çelësat e API-ve nga Metals-API dhe commodities-api
METALS_API_KEY = "YOUR_METALS_API_KEY"
COMMODITIES_API_KEY = "YOUR_COMMODITIES_API_KEY"

def get_gold_price():
    url = f"https://metals-api.com/api/latest?access_key={METALS_API_KEY}&base=USD&symbols=XAU"
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        price = data['rates']['XAU']
        return price
    except Exception as e:
        st.error(f"Gabim në marrjen e çmimit të arit: {e}")
        return None

def get_oil_price():
    url = f"https://commodities-api.com/api/latest?access_key={COMMODITIES_API_KEY}&base=USD&symbols=WTI"
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        price = data['data']['rates']['WTI']
        return price
    except Exception as e:
        st.error(f"Gabim në marrjen e çmimit të naftës: {e}")
        return None

gold_price = get_gold_price()
oil_price = get_oil_price()

if gold_price:
    st.write(f"💰 Çmimi aktual i arit (XAU/USD): ${gold_price:.2f} per ounce")
else:
    st.write("Nuk u morën të dhëna për arin.")

if oil_price:
    st.write(f"⛽ Çmimi aktual i naftës WTI (USD): ${oil_price:.2f} per barrel")
else:
    st.write("Nuk u morën të dhëna për naftën.")
