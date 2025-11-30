import streamlit as st
import pandas as pd

# ======================== KONFIGURIMI BAZË ========================
st.set_page_config(
    page_title="ElBuni Strategy PRO – 70/30 · 3x · TP & SL",
    page_icon="💹",
    layout="wide"
)

# ======================== STILIMI (CSS) ========================
st.markdown("""
<style>
.main {
    background: radial-gradient(circle at top left, #03131f, #020814 50%, #000000 100%);
    color: #f5f5f5;
    font-family: "Segoe UI", system-ui;
}
.elb-card {
    background: rgba(10, 20, 40, 0.9);
    border-radius: 18px;
    padding: 18px 24px;
    border: 1px solid rgba(0, 255, 204, 0.18);
    box-shadow: 0 0 25px rgba(0, 0, 0, 0.5);
}
.elb-title {
    font-size: 34px;
    font-weight: 700;
    color: #00f5d4;
    text-shadow: 0 0 14px rgba(0, 245, 212, 0.6);
    margin-bottom: 6px;
}
.elb-subtitle {
    font-size: 15px;
    color: #cbd5f5;
}
h2, h3 {
    color: #e0f7ff !important;
}
.metric-label {
    font-size: 13px;
    color: #9ca3af;
}
.metric-value {
    font-size: 24px;
    font-weight: 700;
}
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}
.stButton>button {
    border-radius: 999px;
    border: 1px solid rgba(34, 197, 94, 0.6);
    background: radial-gradient(circle at top left, #16a34a, #14532d);
    color: white;
    font-weight: 600;
}
.stButton>button:hover {
    border-color: #22c55e;
    box-shadow: 0 0 18px rgba(34, 197, 94, 0.6);
}
</style>
""", unsafe_allow_html=True)

# ======================== HEADER ========================
st.markdown(
    """
    <div class="elb-card">
        <div class="elb-title">💹 ElBuni Strategy PRO – TP & SL</div>
        <div class="elb-subtitle">
            Model fiks: <b>70% SPOT</b> · <b>30% FUTURES SHORT</b> · <b>Leverage 3x</b>.<br>
            FUTURES ka <b>Take Profit</b> në rënie (−TP%) dhe <b>Stop Loss</b> në ngritje (+SL%).<br>
            Fitimi i futures në TP hidhet në SPOT, pastaj çmimi kthehet në <b>0%</b> → llogaritet fitimi final.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("")

# ======================== PARAMETRAT E FIKSUAR ========================
SPOT_PCT = 70.0        # %
FUTURES_PCT = 30.0     # %
LEVERAGE = 3.0         # x

# ======================== INPUTET ========================
st.markdown("### 📥 Shkruaj investimin, TP dhe SL")

colA, colB, colC = st.columns(3)

with colA:
    investimi_total = st.number_input(
        "💰 Investimi total (USDT)",
        min_value=0.0,
        value=20000.0,
        step=100.0
    )

with colB:
    tp_down_percent = st.number_input(
        "🎯 TP për SHORT (rënia, −%)",
        min_value=0.1,
        max_value=80.0,
        value=2.0,      # ti the minus 2%
        step=0.1
    )

with colC:
    sl_up_percent = st.number_input(
        "🛑 SL për SHORT (ngritja, +%)",
        min_value=0.1,
        max_value=80.0,
        value=5.0,
        step=0.1
    )

st.markdown("")

col_price1, col_price2 = st.columns(2)
with col_price1:
    price_entry = st.number_input(
        "💲 Çmimi hyrës i coinit (opsionale – për coin-at)",
        min_value=0.0,
        value=0.00000457,
        format="%.12f"
    )

st.markdown("---")

# ======================== LLOGARITJET ========================
if investimi_total > 0:
    # Kapitali në spot & futures
    spot_cap = investimi_total * SPOT_PCT / 100.0
    fut_margin = investimi_total * FUTURES_PCT / 100.0
    fut_notional = fut_margin * LEVERAGE

    # ---------- SKENARI TP (RËNIE −tp%) ----------
    d_tp = tp_down_percent / 100.0

    spot_loss_tp = spot_cap * d_tp          # humbja në SPOT në -TP%
    fut_profit_tp = fut_notional * d_tp     # fitimi në FUTURES në -TP%

    spot_value_after_drop = spot_cap * (1 - d_tp)
    spot_value_after_profit = spot_value_after_drop + fut_profit_tp

    # Rikthimi nga -TP% në 0% → factor = 1/(1 - d_tp)
    factor_up_tp = 1.0 / (1.0 - d_tp)
    spot_final_tp = spot_value_after_profit * factor_up_tp

    total_final_tp = spot_final_tp + fut_margin
    total_pnl_final_tp = total_final_tp - investimi_total

    total_at_tp = spot_value_after_drop + fut_margin + fut_profit_tp
    total_pnl_at_tp = total_at_tp - investimi_total

    # coin calculations për TP
    coins_initial_tp = coins_from_profit_tp = coins_total_tp = None
    if price_entry > 0:
        price_tp = price_entry * (1 - d_tp)
        coins_initial_tp = spot_cap / price_entry
        coins_from_profit_tp = fut_profit_tp / price_tp
        coins_total_tp = coins_initial_tp + coins_from_profit_tp

    # ---------- SKENARI SL (NGRITJE +sl%) ----------
    u_sl = sl_up_percent / 100.0

    spot_profit_sl = spot_cap * u_sl        # fitimi në SPOT kur rritet
    fut_loss_sl = fut_notional * u_sl       # humbja në FUTURES short

    spot_value_sl = spot_cap * (1 + u_sl)

    # P&L total në momentin e SL-së
    pnl_sl = spot_profit_sl - fut_loss_sl
    total_sl = investimi_total + pnl_sl

    # ======================== KARTAT E TP & SL ========================
    st.markdown("### 📊 Insight i shpejtë: TP & SL")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown('<div class="elb-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">SPOT fillestar (70%)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{spot_cap:,.2f} USDT</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="elb-card">', unsafe_allow_html=True)
        st.markmarkdown('<div class="metric-label">FUTURES margin (30%)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{fut_margin:,.2f} USDT</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="elb-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-label">TP: Fitimi FUTURES në -{tp_down_percent:.1f}%</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">+{fut_profit_tp:,.2f} USDT</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="elb-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-label">SL: P&L në +{sl_up_percent:.1f}%</div>', unsafe_allow_html=True)
        color_sl = "#22c55e" if pnl_sl >= 0 else "#ef4444"
        sign_sl = "+" if pnl_sl >= 0 else ""
        st.markdown(
            f'<div class="metric-value" style="color:{color_sl};">{sign_sl}{pnl_sl:,.2f} USDT</div>',
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("")

    # ======================== TABELA E SKENARIT TP ========================
    st.markdown("### 🧮 Skenari TP – Çmimi bie −TP%, mbyllet short-i, fitimi hidhet në SPOT dhe çmimi kthehet në 0%")

    tp_rows = [{
        "Investimi total (USDT)": round(investimi_total, 2),
        "SPOT fillestar (USDT)": round(spot_cap, 2),
        "FUTURES margin (USDT)": round(fut_margin, 2),
        "Leverage FUTURES (x)": LEVERAGE,
        "TP (rënia, −%)": tp_down_percent,
        "Fitimi FUTURES në −TP% (USDT)": round(fut_profit_tp, 2),
        "Humbja SPOT në −TP% (USDT)": round(spot_loss_tp, 2),
        "P&L total në −TP% (USDT)": round(total_pnl_at_tp, 2),
        "Fitimi total kur kthehet 0% (USDT)": round(total_pnl_final_tp, 2),
        "Totali final në 0% (USDT)": round(total_final_tp, 2),
    }]

    if coins_total_tp is not None:
        tp_rows[0]["Sasia fillestare (coin)"] = round(coins_initial_tp, 2)
        tp_rows[0]["Coin nga fitimi i futures"] = round(coins_from_profit_tp, 2)
        tp_rows[0]["Sasia totale në 0% (coin)"] = round(coins_total_tp, 2)

    tp_df = pd.DataFrame(tp_rows)
    st.dataframe(tp_df, use_container_width=True)

    # ======================== TABELA E SKENARIT SL ========================
    st.markdown("### 🧨 Skenari SL – Çmimi rritet +SL%, mbyllet short-i me humbje")

    sl_rows = [{
        "Investimi total (USDT)": round(investimi_total, 2),
        "SPOT fillestar (USDT)": round(spot_cap, 2),
        "FUTURES margin (USDT)": round(fut_margin, 2),
        "Leverage FUTURES (x)": LEVERAGE,
        "SL (ngritja, +%)": sl_up_percent,
        "Fitimi SPOT në +SL% (USDT)": round(spot_profit_sl, 2),
        "Humbja FUTURES në +SL% (USDT)": round(fut_loss_sl, 2),
        "P&L total në +SL% (USDT)": round(pnl_sl, 2),
        "Totali i kapitalit në +SL% (USDT)": round(total_sl, 2),
    }]

    sl_df = pd.DataFrame(sl_rows)
    st.dataframe(sl_df, use_container_width=True)

    # ======================== PËRMBLEDHJE ========================
    st.markdown("### 📝 Përmbledhje e skenarëve")

    sign_tp_drop = "+" if total_pnl_at_tp >= 0 else ""
    sign_tp_final = "+" if total_pnl_final_tp >= 0 else ""
    sign_sl_txt = "+" if pnl_sl >= 0 else ""

    st.markdown(f"""
**🎯 TP – Rënia −{tp_down_percent:.1f}%**

- SPOT humb: **{spot_loss_tp:,.2f} USDT**
- FUTURES fiton: **{fut_profit_tp:,.2f} USDT**
- P&L total në momentin e mbylljes së short-it (−TP%): **{sign_tp_drop}{total_pnl_at_tp:,.2f} USDT**

Fitimi i futures hidhet në SPOT. Kur çmimi kthehet prapë në **0%**:
- Fitimi total final i strategjisë: **{sign_tp_final}{total_pnl_final_tp:,.2f} USDT**
- Kapitali total bëhet: **{total_final_tp:,.2f} USDT** (nga {investimi_total:,.2f} USDT)

---

**🛑 SL – Ngritja +{sl_up_percent:.1f}%**

- SPOT fiton: **{spot_profit_sl:,.2f} USDT**
- FUTURES humb: **{fut_loss_sl:,.2f} USDT**
- P&L total në momentin e mbylljes së short-it (SL): **{sign_sl_txt}{pnl_sl:,.2f} USDT**
- Kapitali total në +SL%: **{total_sl:,.2f} USDT**
""")

else:
    st.info("👉 Shkruaj një shumë > 0 te 'Investimi total (USDT)' që të shohësh llogaritjet.")