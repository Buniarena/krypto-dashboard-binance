import streamlit as st
import pandas as pd
from PIL import Image
import os  # për ruajtjen e logos në disk

# ======================== KONFIGURIMI BAZË ========================
st.set_page_config(
    page_title="ElBuni Strategy PRO – TP & SL + Manual + GRID",
    page_icon="💹",
    layout="wide"
)

# ======================== STILIMI ========================
st.markdown("""
<style>
.main {
    background: radial-gradient(circle at top left, #03131f, #020814 50%, #000000 100%);
    color: #eef3f8;
    font-family: "Segoe UI", system-ui;
}
.elb-card {
    background: rgba(10, 20, 40, 0.9);
    border-radius: 18px;
    padding: 18px 24px;
    border: 1px solid rgba(0, 255, 204, 0.18);
    box-shadow: 0 0 22px rgba(0, 0, 0, 0.5);
    margin-bottom: 10px;
}
.elb-title {
    font-size: 34px;
    font-weight: 700;
    color: #00f5d4;
    text-shadow: 0 0 14px rgba(0, 245, 212, 0.6);
}
.metric-label {
    font-size: 13px;
    color: #9ca3af;
}
.metric-value {
    font-size: 22px;
    font-weight: 700;
}
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}
.copy-btn {
    margin-top: 8px;
    padding: 4px 10px;
    border-radius: 999px;
    border: 1px solid rgba(34, 197, 94, 0.8);
    background: radial-gradient(circle at top left, #16a34a, #14532d);
    color: white;
    font-size: 12px;
    cursor: pointer;
}
.copy-btn:hover {
    box-shadow: 0 0 14px rgba(34, 197, 94, 0.8);
}
</style>
""", unsafe_allow_html=True)

# ======================== SIDEBAR – UPLOAD LOGO ========================
with st.sidebar:
    st.markdown("### 🔰 Logo ElBuni")
    uploaded_logo = st.file_uploader(
        "Ngarko logon ElBuni (PNG / JPG)",
        type=["png", "jpg", "jpeg"]
    )

# ======================== LOGO PERSISTENTE NË DISK ========================
LOGO_PATH = "uploads/el_buni_logo.png"
os.makedirs("uploads", exist_ok=True)

if uploaded_logo is not None:
    try:
        with open(LOGO_PATH, "wb") as f:
            f.write(uploaded_logo.getbuffer())
    except Exception as e:
        st.sidebar.write("❌ Nuk u ruajt logoja:", e)

logo_to_show = None
if os.path.exists(LOGO_PATH):
    try:
        logo_to_show = Image.open(LOGO_PATH)
    except:
        logo_to_show = None

# ======================== HEADER ME LOGO ========================
st.markdown("")

if logo_to_show is not None:
    st.image(logo_to_show, use_column_width=False, width=420)
else:
    st.markdown("### 💹 ElBuni Strategy PRO")

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# ======================== TABS ========================
tab_calc, tab_manual, tab_grid = st.tabs(
    ["🧮 Kalkulatori", "📘 Manuali i Strategjisë", "🧱 ElBuni GRID"]
)

# ======================== TAB 1: KALKULATORI KRYESOR ========================
with tab_calc:
    st.markdown("### ⚙️ Zgjedh konfigurimin tënd (Hedging SPOT + FUTURES SHORT)")

    colA, colB, colC = st.columns(3)

    with colA:
        investimi_total = st.number_input(
            "💰 Investimi total (USDT)",
            min_value=0.0,
            value=5000.0,
            step=100.0
        )

    with colB:
        spot_pct = st.slider("📊 SPOT (%)", 0, 100, 70)

    with colC:
        leverage = st.number_input(
            "⚙️ Leverage Futures (x)",
            min_value=1.0,
            max_value=10.0,
            value=2.0,
            step=0.5
        )

    futures_pct = 100 - spot_pct
    st.markdown(f"**📉 FUTURES short (%) = {futures_pct}%**")

    st.markdown("---")

    colTP, colSL = st.columns(2)

    with colTP:
        tp_down_percent = st.number_input(
            "🎯 Take Profit short (rënia −%)",
            min_value=0.1,
            max_value=80.0,
            value=2.0,
            step=0.1
        )

    with colSL:
        sl_up_percent = st.number_input(
            "🛑 Stop Loss short (ngritja +%)",
            min_value=0.1,
            max_value=80.0,
            value=6.0,
            step=0.1
        )

    price_entry = st.number_input(
        "💲 Çmimi hyrës (entry) – si në Binance",
        min_value=0.0,
        value=0.00000457,
        format="%.10f"
    )

    st.markdown("---")

    # ======================== ÇMIMET TP & SL ========================
    if price_entry > 0:
        tp_price = price_entry * (1 - tp_down_percent/100)
        sl_price = price_entry * (1 + sl_up_percent/100)

        st.markdown("### 💲 Çmimet për Binance")

        ct1, ct2 = st.columns(2)

        with ct1:
            st.markdown('<div class="elb-card">📉 Çmimi TP</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{tp_price:.10f}</div>', unsafe_allow_html=True)

        with ct2:
            st.markdown('<div class="elb-card">📈 Çmimi SL</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{sl_price:.10f}</div>', unsafe_allow_html=True)

        # --------- TABELA E ÇMIMEVE PËR +1…+6% DHE −2% ---------
        rows_levels = []
        for i in range(1, 7):
            price_plus = price_entry * (1 + i / 100.0)
            rows_levels.append({
                "Lëvizja": f"+{i}%",
                "Çmimi": f"{price_plus:.10f}"
            })

        price_minus2 = price_entry * (1 - 2 / 100.0)
        rows_levels.append({
            "Lëvizja": "-2%",
            "Çmimi": f"{price_minus2:.10f}"
        })

        df_levels = pd.DataFrame(rows_levels)
        st.markdown("### 📌 Çmimet për lëvizjet % (gati për TP / SL)")
        st.dataframe(df_levels, use_container_width=True)

    else:
        st.info("✋ Shkruaj një çmim hyrës > 0 që të llogariten TP/SL dhe tabela e çmimeve.")

    st.markdown("---")

    # ======================== LLOGARITJET ========================
    if investimi_total > 0:

        spot_cap = investimi_total * spot_pct / 100
        fut_margin = investimi_total * futures_pct / 100
        fut_notional = fut_margin * leverage

        d_tp = tp_down_percent / 100
        u_sl = sl_up_percent / 100

        # ---------- TP ----------
        spot_loss_tp = spot_cap * d_tp
        fut_profit_tp = fut_notional * d_tp

        spot_after_tp = (spot_cap - spot_loss_tp) + fut_profit_tp
        spot_final_tp = spot_after_tp / (1 - d_tp)

        total_final_tp = spot_final_tp + fut_margin
        pnl_total_tp = total_final_tp - investimi_total

        # coin-at nëse kemi entry
        coins_initial = coins_from_fut = coins_total = None
        if price_entry > 0:
            price_after_drop = price_entry * (1 - d_tp)
            if price_after_drop > 0:
                coins_initial = spot_cap / price_entry
                coins_from_fut = fut_profit_tp / price_after_drop
                coins_total = coins_initial + coins_from_fut

        # ---------- SL ----------
        spot_profit_sl = spot_cap * u_sl
        fut_loss_sl = fut_notional * u_sl

        pnl_sl = spot_profit_sl - fut_loss_sl
        total_sl = investimi_total + pnl_sl

        # ======================== TABELAT ========================
        st.markdown("### 📘 TP – rikthimi në 0%")
        tp_row = {
            "Investimi total": investimi_total,
            "SPOT %": spot_pct,
            "FUTURES %": futures_pct,
            "Leverage": leverage,
            "TP −%": tp_down_percent,
            "Fitimi FUTURES": fut_profit_tp,
            "Humbja SPOT": spot_loss_tp,
            "Totali final": total_final_tp,
            "P&L final": pnl_total_tp
        }
        if coins_total is not None:
            tp_row["Coin fillestarë"] = coins_initial
            tp_row["Coin nga FUTURES"] = coins_from_fut
            tp_row["Coin total në 0%"] = coins_total

        tp_df = pd.DataFrame([tp_row])
        st.dataframe(tp_df, use_container_width=True)

        st.markdown("### 📕 SL – ngritja +%")
        sl_df = pd.DataFrame([{
            "Investimi total": investimi_total,
            "SPOT %": spot_pct,
            "FUTURES %": futures_pct,
            "Leverage": leverage,
            "SL +%": sl_up_percent,
            "Fitimi SPOT": spot_profit_sl,
            "Humbja FUTURES": fut_loss_sl,
            "Totali final": total_sl,
            "P&L final": pnl_sl
        }])
        st.dataframe(sl_df, use_container_width=True)

        # ======================== PËRMBLEDHJE ========================
        sign_tp = "+" if pnl_total_tp >= 0 else ""
        sign_sl = "+" if pnl_sl >= 0 else ""

        st.markdown("### 🧾 Përmbledhja e konfigurimit tënd")

        st.markdown(f"""
**💰 Çfarë ke futur:**
- Investimi total: **{investimi_total:,.2f} USDT**
- SPOT ({spot_pct}%): **{spot_cap:,.2f} USDT**
- FUTURES margin ({futures_pct}%): **{fut_margin:,.2f} USDT**
- Leverage i futures: **x{leverage}**
""")

        st.markdown("#### 🎯 Skenari TP – çmimi bie dhe kthehet në 0%")

        st.markdown(f"""
- Rënia e çmimit: **-{tp_down_percent:.2f}%**
- Humbja në SPOT: **{spot_loss_tp:,.2f} USDT**
- Fitimi në FUTURES: **{fut_profit_tp:,.2f} USDT**
- Kapitali final në rikthim: **{total_final_tp:,.2f} USDT**
- P&L total: **{sign_tp}{pnl_total_tp:,.2f} USDT**
""")

        if coins_total is not None:
            st.markdown(f"""
**📈 Coin-at:**
- Coin fillestarë: **{coins_initial:,.2f}**
- Coin nga futures: **{coins_from_fut:,.2f}**
- Coin total: **{coins_total:,.2f}**
""")

        st.markdown("#### 🛑 Skenari SL – çmimi rritet")

        st.markdown(f"""
- Ngritja e çmimit: **+{sl_up_percent:.2f}%**
- Fitimi SPOT: **{spot_profit_sl:,.2f} USDT**
- Humbja FUTURES: **{fut_loss_sl:,.2f} USDT**
- P&L final: **{sign_sl}{pnl_sl:,.2f} USDT**
- Kapitali final: **{total_sl:,.2f} USDT**
""")

# ======================== TAB 2: MANUALI ========================
with tab_manual:
    st.markdown("## 📘 Manuali i Strategjisë ElBuni (lev 2x)")

    st.markdown("""
### 1️⃣ Çfarë është ElBuni Strategy?
Një strategji e balancuar SPOT + FUTURES SHORT ku fiton:
- Kur bie çmimi  
- Kur rritet çmimi  
- Kur kthehet në 0% (fiton coin)

### 2️⃣ Struktura bazë
- SPOT: 70%  
- FUTURES: 30%  
- Leverage: 2x  

### 3️⃣ Çfarë ndodh në TP?
- FUTURES fiton  
- SPOT humbet pak  
- Fitimi i futures hidhet te SPOT  
➡️ Rezultat: Më shumë coin kur rikthehet çmimi në 0%

### 4️⃣ Çfarë ndodh në SL?
- SPOT fiton shumë  
- FUTURES humb  
➡️ Me lev 2x zakonisht afër zeros ose fitim i vogël

### 5️⃣ Avantazhet
- Rrezik shumë i ulët  
- TP të shpejta  
- Shton coin çdo cikël  
- Perfect për tregje me valë  
""")

# ======================== TAB 3: ELBUNI GRID (SPOT) ========================
with tab_grid:
    st.markdown("## 🧱 ElBuni GRID – Mini-Grid SPOT për PEPE/XVG")

    st.markdown("""
Strategji shumë e sigurt për luhatje të vogla:

- Vendos disa **BUY** në rënie  
- Vendos **TP** të vegjël për çdo nivel  
- Çdo cikël sjell fitim të vogël + shtim të coinit  
""")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        total_cap_grid = st.number_input(
            "💰 Kapitali për GRID (USDT)",
            min_value=10.0,
            value=200.0,
            step=10.0,
            key="grid_cap"
        )

        step_percent = st.number_input(
            "📉 Distanca mes BUY-ve (−%)",
            min_value=0.1,
            max_value=50.0,
            value=1.0,
            step=0.1,
            key="grid_step"
        )

    with col2:
        grid_levels = st.number_input(
            "📊 Numri i niveleve",
            min_value=1,
            max_value=20,
            value=5,
            key="grid_levels"
        )

        tp_percent = st.number_input(
            "📈 TP për çdo nivel (+%)",
            min_value=0.1,
            max_value=50.0,
            value=1.0,
            step=0.1,
            key="grid_tp"
        )

    entry_grid = st.number_input(
        "💲 Çmimi hyrës (PEPE/XVG)",
        min_value=0.0,
        value=0.00000457,
        format="%.10f",
        key="grid_entry"
    )

    st.markdown("---")

    if entry_grid > 0:
        amount_per_grid = total_cap_grid / grid_levels

        buy_prices = []
        tp_prices = []
        coins = []
        profits = []

        for i in range(grid_levels):
            buy_price = entry_grid * (1 - (step_percent/100) * i)
            tp_price = buy_price * (1 + tp_percent/100)

            buy_prices.append(buy_price)
            tp_prices.append(tp_price)

            coin_amount = amount_per_grid / buy_price
            coins.append(coin_amount)

            profit_usdt = coin_amount * (tp_price - buy_price)
            profits.append(profit_usdt)

        df_grid = pd.DataFrame({
            "Niveli": list(range(1, grid_levels + 1)),
            "BUY Price": buy_prices,
            "TP Price": tp_prices,
            "Coins": coins,
            "Profit/Level (USDT)": profits
        })

        st.markdown("### 📊 Tabela e GRID-it")
        st.dataframe(df_grid, use_container_width=True)

        total_profit = sum(profits)
        total_coins = sum(coins)

        st.markdown("### 📈 Totali i GRID-it")
        colg1, colg2 = st.columns(2)
        with colg1:
            st.metric("Fitimi total (USDT) nëse preken të gjitha TP-të", f"{total_profit:,.4f}")
        with colg2:
            st.metric("Coin total që blihen në gjithë GRID-in", f"{total_coins:,.4f}")
    else:
        st.info("🪙 Shkruaj një çmim hyrës > 0 për të llogaritur grid-in.")

# ===================== SQARIMI FINAL – PREMIUM POSHTË FAQES ========================
st.markdown("<hr>", unsafe_allow_html=True)

st.markdown("""
<div class="elb-card" style="
    margin-top: 20px;
    border-color: rgba(250, 204, 21, 0.6);
    box-shadow: 0 0 25px rgba(250, 204, 21, 0.35);
">
  <div class="elb-title" style="font-size: 26px; margin-bottom: 10px;">
    🧩 SQARIMI FINAL – SI FITON STRATEGJIA ELBUNI
  </div>
  <div style="font-size: 15px; color: #e5e7eb; line-height: 1.6;">
    <b>🔥 Fiton edhe kur bie – edhe kur ngrihet</b><br/>
    • Në <b>TP (rënia)</b> → FUTURES fiton, SPOT humbet pak → TI fiton coin.<br/>
    • Në <b>SL (ngritja)</b> → SPOT fiton shumë, FUTURES humb pak → TI del afër zeros ose në fitim të vogël.<br/><br/>

    <b>🟩 Pse është e fuqishme?</b><br/>
    ✔ Shton coin në çdo cikël<br/>
    ✔ Fiton kur rikthehet çmimi në 0%<br/>
    ✔ Leverage 2x është shumë i sigurt<br/>
    ✔ Mbrojtje ndaj luhatjeve<br/><br/>

    <b>🎯 Afatgjatë:</b><br/>
    🔵 TP të shpeshta → fitim + shtim coin<br/>
    🔵 SL të rralla → humbje të vogla<br/>
    🔵 Kapital që rritet pa rrezik likuidimi<br/><br/>

    Kjo e bën <b>ElBuni Strategy</b> + <b>ElBuni GRID</b>
    një paketë të plotë profesionale për menaxhimin e riskut në kripto.
  </div>
</div>
""", unsafe_allow_html=True)
```0