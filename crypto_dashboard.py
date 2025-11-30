import streamlit as st
import pandas as pd

st.set_page_config(page_title="ElBuni Strategy – Hedging Calculator", layout="centered")

st.title("💹 ElBuni Strategy – Hedging Calculator (Spot + Futures Short)")

st.markdown("""
Ky kalkulator llogarit strategjinë **ElBuni**:
- Ti fus investimin total
- Ndahet në **SPOT** dhe **FUTURES short**
- Zgjedh sa % rënie pret (–X%) ku mbyll short-in
- Fitimi i futures hidhet në SPOT
- Pastaj çmimi kthehet në **0%**  
➡ Llogaritet automatikisht:
- Fitimi i futures
- Humbja e spot
- P&L total në –X%
- Fitimi final kur çmimi kthehet në 0%
""")

st.markdown("---")

# ======================== INPUTET ========================
colA, colB = st.columns(2)

with colA:
    investimi_total = st.number_input(
        "💰 Investimi total (USDT)",
        min_value=0.0,
        value=20000.0,
        step=100.0
    )
    spot_pct = st.slider("📊 Përqindja në SPOT (%)", 0, 100, 70)
    leverage = st.number_input(
        "⚙️ Leverage për FUTURES (x)",
        min_value=1.0,
        value=2.0,
        step=0.5
    )

with colB:
    futures_pct = 100 - spot_pct
    st.write(f"📉 Përqindja në FUTURES: **{futures_pct}%**")
    drop_percent = st.number_input(
        "📉 Rënia ku mbyll SHORT-in (–%)",
        min_value=0.1,
        max_value=80.0,
        value=4.0,
        step=0.1
    )
    price_entry = st.number_input(
        "💲 Çmimi hyrës i coinit (opsionale, për të llogaritur sasinë)",
        min_value=0.0,
        value=0.00000457,
        format="%.12f"
    )

st.markdown("---")

# ======================== LLOGARITJET ========================
if investimi_total > 0:
    d = drop_percent / 100.0

    # Kapitali në spot & futures
    spot_cap = investimi_total * spot_pct / 100.0      # sa para në SPOT
    fut_margin = investimi_total * futures_pct / 100.0 # margin në FUTURES
    fut_notional = fut_margin * leverage               # pozicioni total short

    # Në -X% rënie
    spot_loss_drop = spot_cap * d                      # humbja në SPOT (USDT)
    fut_profit_drop = fut_notional * d                 # fitimi në FUTURES (USDT)

    # Vlera e spot në -X%
    spot_value_after_drop = spot_cap * (1 - d)
    # Fitimi i futures hidhet në SPOT në çmimin e rënies
    spot_value_after_profit = spot_value_after_drop + fut_profit_drop

    # Rikthimi nga -X% në 0% → rritje faktori = 1/(1-d)
    factor_up = 1.0 / (1.0 - d)
    spot_final = spot_value_after_profit * factor_up

    # Futures margin mbetet e njëjtë (profitin e kemi kaluar në SPOT)
    total_final = spot_final + fut_margin
    total_pnl_final = total_final - investimi_total

    # Totali në momentin e -X% (kur mbyll short-in)
    total_at_drop = spot_value_after_drop + fut_margin + fut_profit_drop
    total_pnl_drop = total_at_drop - investimi_total

    # Nëse kemi çmim hyrës, llogarisim edhe sasinë e coinit
    coins_initial = coins_from_profit = coins_total = None
    if price_entry > 0:
        price_drop = price_entry * (1 - d)
        coins_initial = spot_cap / price_entry               # sasia në fillim
        coins_from_profit = fut_profit_drop / price_drop     # coin-a nga fitimi i futures
        coins_total = coins_initial + coins_from_profit      # sasia totale pas hedhjes së fitimit

    # Tabela e rezultateve
    calc_rows = [{
        "Investimi total (USDT)": round(investimi_total, 2),
        "SPOT fillestar (USDT)": round(spot_cap, 2),
        "FUTURES margin (USDT)": round(fut_margin, 2),
        "Leverage FUTURES": leverage,
        "Rënia ku mbyllet short (%)": drop_percent,
        "Fitimi FUTURES në -X% (USDT)": round(fut_profit_drop, 2),
        "Humbja SPOT në -X% (USDT)": round(spot_loss_drop, 2),
        "P&L total në -X% (USDT)": round(total_pnl_drop, 2),
        "Fitimi total kur kthehet 0% (USDT)": round(total_pnl_final, 2),
        "Totali final në 0% (USDT)": round(total_final, 2),
    }]

    if coins_total is not None:
        calc_rows[0]["Sasia fillestare (coin)"] = round(coins_initial, 2)
        calc_rows[0]["Coin nga fitimi i futures"] = round(coins_from_profit, 2)
        calc_rows[0]["Sasia totale në 0% (coin)"] = round(coins_total, 2)

    calc_df = pd.DataFrame(calc_rows)

    st.subheader("📊 Rezultatet e ElBuni Strategy për këtë skenar")
    st.dataframe(calc_df)

    st.markdown(f"""
**🧾 Përmbledhje:**

- Investimi total: **{investimi_total:.2f} USDT**
- SPOT fillestar: **{spot_cap:.2f} USDT** ({spot_pct}%)
- FUTURES margin: **{fut_margin:.2f} USDT** ({futures_pct}%)
- Leverage: **x{leverage}**
- Rënia ku mbyllet short: **-{drop_percent}%**

**Në -{drop_percent}% rënie:**
- Fitimi i FUTURES: **{fut_profit_drop:.2f} USDT**
- Humbja e SPOT: **{spot_loss_drop:.2f} USDT**
- P&L total në atë moment: **{total_pnl_drop:.2f} USDT**

**Kur çmimi kthehet prapë në 0%:**
- Fitimi total final: **{total_pnl_final:.2f} USDT**
- Totali final i kapitalit: **{total_final:.2f} USDT**
""")
else:
    st.info("👉 Shkruaj një shumë > 0 në 'Investimi total' për të parë llogaritjet.")