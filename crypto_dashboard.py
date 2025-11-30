import streamlit as st
import pandas as pd

# ======================== KONFIGURIMI BAZË ========================
st.set_page_config(
    page_title="ElBuni Strategy PRO – 70/30 · 3x · -2%",
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
        <div class="elb-title">💹 ElBuni Strategy PRO – Calculator</div>
        <div class="elb-subtitle">
            Model fiks: <b>70% SPOT</b> · <b>30% FUTURES SHORT</b> · <b>Leverage 3x</b> ·
            short mbyllet në <b>−2%</b>, fitimi i futures hidhet në SPOT, pastaj çmimi kthehet në <b>0%</b>.
            <br>Ti shkruan vetëm <b>investimin</b> dhe (opsionale) <b>çmimin e coinit</b>.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("")

# ======================== PARAMETRAT E FIKSUAR ========================
SPOT_PCT = 70          # %
FUTURES_PCT = 30       # %
LEVERAGE = 3.0         # x
DROP_PERCENT = 2.0     # %

# ======================== INPUTET ========================
st.markdown("### 📥 Shkruaj investimin dhe (nëse do) çmimin e coinit")

colA, colB = st.columns(2)

with colA:
    investimi_total = st.number_input(
        "💰 Investimi total (USDT)",
        min_value=0.0,
        value=20000.0,
        step=100.0
    )

with colB:
    price_entry = st.number_input(
        "💲 Çmimi hyrës i coinit (opsionale – për coin-at)",
        min_value=0.0,
        value=0.00000457,
        format="%.12f"
    )

st.markdown("---")

# ======================== LLOGARITJET ========================
if investimi_total > 0:
    d = DROP_PERCENT / 100.0

    # Kapitali në spot & futures
    spot_cap = investimi_total * SPOT_PCT / 100.0
    fut_margin = investimi_total * FUTURES_PCT / 100.0
    fut_notional = fut_margin * LEVERAGE

    # Në -2% rënie
    spot_loss_drop = spot_cap * d
    fut_profit_drop = fut_notional * d

    spot_value_after_drop = spot_cap * (1 - d)
    spot_value_after_profit = spot_value_after_drop + fut_profit_drop

    # Rikthimi nga -2% në 0% → factor = 1/(1-0.02)
    factor_up = 1.0 / (1.0 - d)
    spot_final = spot_value_after_profit * factor_up

    total_final = spot_final + fut_margin
    total_pnl_final = total_final - investimi_total

    total_at_drop = spot_value_after_drop + fut_margin + fut_profit_drop
    total_pnl_drop = total_at_drop - investimi_total

    # Coin llogaritjet (nëse ka cmim hyrës)
    coins_initial = coins_from_profit = coins_total = None
    if price_entry > 0:
        price_drop = price_entry * (1 - d)
        coins_initial = spot_cap / price_entry
        coins_from_profit = fut_profit_drop / price_drop
        coins_total = coins_initial + coins_from_profit

    # ======================== INSIGHT KARTAT ========================
    st.markdown("### 📊 Insight i shpejtë")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown('<div class="elb-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">SPOT fillestar (70%)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{spot_cap:,.2f} USDT</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="elb-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">FUTURES margin (30%)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{fut_margin:,.2f} USDT</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="elb-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-label">Fitimi FUTURES në -{DROP_PERCENT:.1f}%</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">+{fut_profit_drop:,.2f} USDT</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="elb-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Fitimi total final në 0%</div>', unsafe_allow_html=True)
        color_pnl = "#22c55e" if total_pnl_final >= 0 else "#ef4444"
        sign = "+" if total_pnl_final >= 0 else ""
        st.markdown(
            f'<div class="metric-value" style="color:{color_pnl};">{sign}{total_pnl_final:,.2f} USDT</div>',
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("")

    # ======================== TABELA ========================
    st.markdown("### 🧮 Detajet e plota të skenarit ElBuni (70/30 · 3x · -2%)")

    calc_rows = [{
        "Investimi total (USDT)": round(investimi_total, 2),
        "SPOT fillestar (USDT)": round(spot_cap, 2),
        "FUTURES margin (USDT)": round(fut_margin, 2),
        "Leverage FUTURES (x)": LEVERAGE,
        "Rënia ku mbyllet short (%)": DROP_PERCENT,
        "Fitimi FUTURES në -2% (USDT)": round(fut_profit_drop, 2),
        "Humbja SPOT në -2% (USDT)": round(spot_loss_drop, 2),
        "P&L total në -2% (USDT)": round(total_pnl_drop, 2),
        "Fitimi total kur kthehet 0% (USDT)": round(total_pnl_final, 2),
        "Totali final në 0% (USDT)": round(total_final, 2),
    }]

    if coins_total is not None:
        calc_rows[0]["Sasia fillestare (coin)"] = round(coins_initial, 2)
        calc_rows[0]["Coin nga fitimi i futures"] = round(coins_from_profit, 2)
        calc_rows[0]["Sasia totale në 0% (coin)"] = round(coins_total, 2)

    calc_df = pd.DataFrame(calc_rows)
    st.dataframe(calc_df, use_container_width=True)

    # ======================== PËRMBLEDHJE ========================
    st.markdown("### 📝 Përmbledhje e skenarit")

    sign_drop = "+" if total_pnl_drop >= 0 else ""
    sign_final = "+" if total_pnl_final >= 0 else ""

    st.markdown(f"""
- **Modeli ElBuni fiks:** 70% SPOT · 30% FUTURES · Leverage 3× · short mbyllet në **−2%**.
- Në rënien **−2%**:
  - SPOT humb: **{spot_loss_drop:,.2f} USDT**
  - FUTURES fiton: **{fut_profit_drop:,.2f} USDT**
  - P&L total në atë moment: **{sign_drop}{total_pnl_drop:,.2f} USDT**

- Fitimi i futures hidhet në SPOT.
- Kur çmimi kthehet në **0%**:
  - Fitimi total final: **{sign_final}{total_pnl_final:,.2f} USDT**
  - Kapitali total bëhet: **{total_final:,.2f} USDT** (nga {investimi_total:,.2f} USDT)
""")

    if coins_total is not None:
        st.markdown(f"""
**Niveli i coinit (me çmimin hyrës {price_entry:.12f}):**
- Coin-a fillestarë: **{coins_initial:,.2f}**
- Coin-a nga fitimi i futures: **{coins_from_profit:,.2f}**
- Totali i coin-it kur çmimi kthehet në 0%: **{coins_total:,.2f}**
""")

else:
    st.info("👉 Shkruaj një shumë > 0 te 'Investimi total (USDT)' që të shohësh llogaritjet.")