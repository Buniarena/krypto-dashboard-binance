import streamlit as st
import pandas as pd
from PIL import Image

# ======================== KONFIGURIMI BAZË ========================
st.set_page_config(
    page_title="ElBuni Strategy PRO – TP & SL + Binance Prices + Manual",
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
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
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

# ======================== HEADER ME LOGO ========================
st.markdown("")

if uploaded_logo is not None:
    try:
        logo = Image.open(uploaded_logo)
        st.image(logo, use_column_width=False, width=420)
    except Exception as e:
        st.markdown("### 💹 ElBuni Strategy PRO")
        st.write("Logo error:", str(e))
else:
    st.markdown("### 💹 ElBuni Strategy PRO")

st.markdown("""
<div class="elb-card">
    <div class="elb-title">💹 ElBuni Strategy PRO</div>
    <div style="font-size:15px;color:#cbd5f5;">
        Kalkulator + Manual për strategjinë hedging: SPOT + FUTURES SHORT, TP & SL, dhe çmimet gati për Binance.
        <br/>Përdor tabat më poshtë për të llogaritur dhe për të lexuar shpjegimin e plotë.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("")

# ======================== TABS ========================
tab_calc, tab_manual = st.tabs(["🧮 Kalkulatori", "📘 Manuali i Strategjisë"])

# ======================== TAB 1: KALKULATORI ========================
with tab_calc:
    st.markdown("### ⚙️ Zgjedh konfigurimin tënd")

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
        format="%.12f"
    )

    st.markdown("---")

    # ======================== ÇMIMET TP & SL ========================
    if price_entry > 0:
        tp_price = price_entry * (1 - tp_down_percent/100)
        sl_price = price_entry * (1 + sl_up_percent/100)

        st.markdown("### 💲 Çmimet që shkruan në Binance")

        ct1, ct2 = st.columns(2)

        with ct1:
            st.markdown('<div class="elb-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">📉 Çmimi TP</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{tp_price:.12f}</div>', unsafe_allow_html=True)

        with ct2:
            st.markdown('<div class="elb-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">📈 Çmimi SL</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{sl_price:.12f}</div>', unsafe_allow_html=True)

    else:
        st.info("Shkruaj entry > 0")

    st.markdown("---")

    # ======================== LLOGARITJET TP & SL ========================
    if investimi_total > 0:

        spot_cap = investimi_total * spot_pct / 100
        fut_margin = investimi_total * futures_pct / 100
        fut_notional = fut_margin * leverage

        d_tp = tp_down_percent / 100
        u_sl = sl_up_percent / 100

        # TP
        spot_loss_tp = spot_cap * d_tp
        fut_profit_tp = fut_notional * d_tp

        spot_after_tp = (spot_cap - spot_loss_tp) + fut_profit_tp
        spot_final_tp = spot_after_tp / (1 - d_tp)

        total_final_tp = spot_final_tp + fut_margin
        pnl_total_tp = total_final_tp - investimi_total

        # SL
        spot_profit_sl = spot_cap * u_sl
        fut_loss_sl = fut_notional * u_sl

        pnl_sl = spot_profit_sl - fut_loss_sl
        total_sl = investimi_total + pnl_sl

        # ======================== TABELAT ========================
        st.markdown("### 📘 TP – rikthimi në 0%")
        tp_df = pd.DataFrame([{
            "Investimi total": investimi_total,
            "SPOT %": spot_pct,
            "FUTURES %": futures_pct,
            "Leverage": leverage,
            "TP −%": tp_down_percent,
            "Fitimi FUTURES": fut_profit_tp,
            "Humbja SPOT": spot_loss_tp,
            "Totali final": total_final_tp,
            "P&L final": pnl_total_tp
        }])

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

# ======================== TAB 2: MANUALI ========================
with tab_manual:
    st.markdown("## 📘 Manuali i Strategjisë ElBuni (shembull me lev 2x)")

    st.markdown("""
### 1️⃣ Çfarë është ElBuni Strategy?

Strategji hedging ku ti kombinon:

- **SPOT** (blerje normale)
- **FUTURES SHORT** (parashikon rënie)

Qëllimi:
- Fiton kur bie çmimi
- Fiton coin kur kthehet në 0%
- Humbja në rritje kontrollohet nga SPOT

---

### 2️⃣ Shembull me lev 2x
- Investimi: **5000 USDT**
- SPOT: **70% = 3500 USDT**
- FUTURES margin: **30% = 1500 USDT**
- Pozicion SHORT total: **3000 USDT**

---

### 3️⃣ Çfarë ndodh në TP (p.sh −2%)?
- SPOT humbet pak
- FUTURES fiton pothuajse sa humbet spot
- Fitimi i futures kthehet në SPOT
- Kur çmimi ngjitet përsëri → del me më shumë coin

---

### 4️⃣ Çfarë ndodh në SL (p.sh +6%)?
- SPOT fiton
- FUTURES humb
- P&L neto shpesh del **pak fitim** me lev 2x

---

### 5️⃣ Formulat e çmimeve

- **TP** = entry × (1 − TP%)
- **SL** = entry × (1 + SL%)

---

### 6️⃣ Avantazhi (EDGE)
- Lev 2x nuk djeg kapitalin si lev të lartë
- TP është më i lehtë për t’u goditur
- SL shpesh del neutrale / fitim i vogël
- Shton coin në çdo cikël të rënies

---

### 7️⃣ Udhëzimet

1. Vendos investimin
2. Zgjidh SPOT/FUTURES %
3. Vendos Leverage
4. Shkruaj çmimin entry
5. Kopjo TP & SL
6. Kontrollo tabelat e TP/SL

---

### 8️⃣ Këshilla

- Mos e përdor 24/7
- Përdor vetëm kur ka luhatje
- Mos e përdor në super-bull afatgjatë
- Testoje me shuma të vogla para kapitaleve të mëdha
""")