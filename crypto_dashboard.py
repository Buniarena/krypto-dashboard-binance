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
</style>
""", unsafe_allow_html=True)

# ======================== SIDEBAR – LOGO ========================
with st.sidebar:
    st.markdown("### Logo ElBuni")
    uploaded_logo = st.file_uploader(
        "Ngarko logon (PNG / JPG)",
        type=["png", "jpg", "jpeg"]
    )

# ======================== LOGO PERSISTENTE ========================
LOGO_PATH = "uploads/el_buni_logo.png"
os.makedirs("uploads", exist_ok=True)

if uploaded_logo is not None:
    with open(LOGO_PATH, "wb") as f:
        f.write(uploaded_logo.getbuffer())

logo_to_show = Image.open(LOGO_PATH) if os.path.exists(LOGO_PATH) else None

# ======================== HEADER ========================
if logo_to_show is not None:
    st.image(logo_to_show, width=420)
else:
    st.markdown("### 💹 ElBuni Strategy PRO")

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# ======================== TABS ========================
tab_calc, tab_manual, tab_grid = st.tabs(
    ["🧮 Kalkulatori", "📘 Manuali", "🧱 ElBuni GRID"]
)

# ======================== TAB: KALKULATORI ========================
with tab_calc:

    st.markdown("### ⚙️ Konfigurimi kryesor")

    colA, colB, colC = st.columns(3)

    with colA:
        investimi_total = st.number_input(
            "Investimi total (USDT)", 0.0, value=5000.0, step=100.0
        )

    with colB:
        spot_pct = st.slider("SPOT (%)", 0, 100, 70)

    with colC:
        leverage = st.number_input(
            "Leverage Futures (x)", 1.0, 10.0, value=2.0, step=0.5
        )

    futures_pct = 100 - spot_pct
    st.markdown(f"**FUTURES short (%) = {futures_pct}%**")

    st.markdown("---")

    colTP, colSL = st.columns(2)

    with colTP:
        tp_down_percent = st.number_input(
            "Take Profit short (rënia −%)", 0.1, 80.0, 2.0, 0.1
        )

    with colSL:
        sl_up_percent = st.number_input(
            "Stop Loss short (ngritja +%)", 0.1, 80.0, 6.0, 0.1
        )

    price_entry = st.number_input(
        "Çmimi hyrës (entry)", 0.0, value=0.00000457, format="%.10f"
    )

    st.markdown("---")

    # ======================== ÇMIMET ========================
    if price_entry > 0:

        tp_price = price_entry * (1 - tp_down_percent/100)
        sl_price = price_entry * (1 + sl_up_percent/100)

        st.markdown("### Çmimet TP & SL")
        st.write("TP:", f"{tp_price:.10f}")
        st.write("SL:", f"{sl_price:.10f}")

        rows = []
        for i in range(1, 7):
            rows.append({
                "Lëvizja": f"+{i}%",
                "Çmimi": f"{price_entry * (1 + i/100):.10f}"
            })

        rows.append({
            "Lëvizja": "-2%",
            "Çmimi": f"{price_entry * 0.98:.10f}"
        })

        df_levels = pd.DataFrame(rows)
        st.markdown("### Tabela e çmimeve për lëvizjet %")
        st.dataframe(df_levels, use_container_width=True)

    st.markdown("---")

    # ======================== LLOGARITJE ========================
    if investimi_total > 0:

        spot_cap = investimi_total * spot_pct / 100
        fut_margin = investimi_total * futures_pct / 100
        fut_notional = fut_margin * leverage

        d = tp_down_percent / 100
        u = sl_up_percent / 100

        # TP
        spot_loss_tp = spot_cap * d
        fut_profit_tp = fut_notional * d
        spot_after_tp = (spot_cap - spot_loss_tp) + fut_profit_tp
        spot_final_tp = spot_after_tp / (1 - d)
        total_final_tp = spot_final_tp + fut_margin
        pnl_tp = total_final_tp - investimi_total

        # SL
        spot_profit_sl = spot_cap * u
        fut_loss_sl = fut_notional * u
        pnl_sl = spot_profit_sl - fut_loss_sl
        total_sl = investimi_total + pnl_sl

        # Output
        st.markdown("### Rezultatet")
        st.write("P&L TP:", pnl_tp)
        st.write("P&L SL:", pnl_sl)

# ======================== TAB: MANUAL ========================
with tab_manual:
    st.markdown("## Manuali i Strategjisë ElBuni")
    st.write("""
Strategjia ElBuni përdor SPOT + FUTURES SHORT për të krijuar hedging të qëndrueshëm.
Behet fitim në TP dhe mbrohet kapitali në SL.
""")

# ======================== TAB: GRID ========================
with tab_grid:

    st.markdown("## ElBuni GRID – Mini Grid Spot")

    total_cap_grid = st.number_input("Kapitali GRID", 10.0, value=200.0)
    step_percent = st.number_input("Distanca ndërmjet BUY (−%)", 0.1, 50.0, value=1.0)
    grid_levels = st.number_input("Nivelet", 1, 20, value=5)
    tp_percent = st.number_input("TP për nivel (+%)", 0.1, 20.0, value=1.0)
    entry_grid = st.number_input("Çmimi hyrës", 0.0, value=0.00000457, format="%.10f")

    if entry_grid > 0:

        amount_per_grid = total_cap_grid / grid_levels
        rows = []

        for i in range(grid_levels):
            buy = entry_grid * (1 - (step_percent/100) * i)
            sell = buy * (1 + tp_percent/100)
            coins = amount_per_grid / buy
            profit = coins * (sell - buy)

            rows.append({
                "Niveli": i+1,
                "BUY": buy,
                "TP": sell,
                "Coins": coins,
                "Profit": profit
            })

        df_grid = pd.DataFrame(rows)
        st.dataframe(df_grid, use_container_width=True)


# ======================== FUND ========================