import streamlit as st
import pandas as pd

# ======================== KONFIGURIMI BAZË ========================
st.set_page_config(
    page_title="ElBuni Strategy PRO v3 – TP & SL + Binance Prices",
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
</style>
""", unsafe_allow_html=True)

# ======================== HEADER ========================
st.markdown("""
<div class="elb-card">
    <div class="elb-title">💹 ElBuni Strategy PRO v3</div>
    <div style="font-size:15px;color:#cbd5f5;">
        Ti vet zgjedh: SPOT %, FUTURES %, Leverage, TP (−%), SL (+%) dhe investimin total.<br>
        App-i llogarit fitimet/humbjet për TP & SL dhe të jep çmimet e sakta TP/SL për t'u shkruar në Binance.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("")

# ======================== INPUTET KRYESORE ========================
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
        value=3.0,
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

# ======================== ÇMIMET TP & SL PËR BINANCE ========================
if price_entry > 0:
    tp_price = price_entry * (1 - tp_down_percent / 100.0)
    sl_price = price_entry * (1 + sl_up_percent / 100.0)

    st.markdown("### 💲 Çmimet që shkruan në Binance (TP & SL)")

    ctp, csl = st.columns(2)

    with ctp:
        st.markdown('<div class="elb-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">📉 Çmimi TP (rënia −%)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{tp_price:.12f}</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <button class="copy-btn"
                onclick="navigator.clipboard.writeText('{tp_price:.12f}')">
                Kopjo TP në clipboard
            </button>
            """,
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with csl:
        st.markdown('<div class="elb-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">📈 Çmimi SL (ngritja +%)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{sl_price:.12f}</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <button class="copy-btn"
                onclick="navigator.clipboard.writeText('{sl_price:.12f}')">
                Kopjo SL në clipboard
            </button>
            """,
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

else:
    tp_price = None
    sl_price = None
    st.info("✋ Shkruaj një çmim hyrës > 0 që të llogariten çmimet TP/SL për Binance.")

st.markdown("---")

# ======================== LLOGARITJET PËR TP & SL ========================
if investimi_total > 0:
    # Bazë
    spot_cap = investimi_total * spot_pct / 100.0
    fut_margin = investimi_total * futures_pct / 100.0
    fut_notional = fut_margin * leverage

    # ---------- TP (rënia −%) ----------
    d_tp = tp_down_percent / 100.0

    spot_loss_tp = spot_cap * d_tp
    fut_profit_tp = fut_notional * d_tp

    spot_after_drop = spot_cap * (1 - d_tp)
    spot_after_profit = spot_after_drop + fut_profit_tp

    factor_up_tp = 1.0 / (1.0 - d_tp)
    spot_final_tp = spot_after_profit * factor_up_tp

    total_final_tp = spot_final_tp + fut_margin
    pnl_total_tp = total_final_tp - investimi_total

    coins_initial = coins_from_tp = coins_total_tp = None
    if price_entry > 0:
        price_tp = price_entry * (1 - d_tp)
        coins_initial = spot_cap / price_entry
        coins_from_tp = fut_profit_tp / price_tp
        coins_total_tp = coins_initial + coins_from_tp

    # ---------- SL (ngritja +%) ----------
    u_sl = sl_up_percent / 100.0

    spot_profit_sl = spot_cap * u_sl
    fut_loss_sl = fut_notional * u_sl

    pnl_sl = spot_profit_sl - fut_loss_sl
    total_sl = investimi_total + pnl_sl

    # ======================== INSIGHT ========================
    st.markdown("### 📊 Insight i shpejtë i skenarit")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown('<div class="elb-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">SPOT fillestar</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{spot_cap:,.2f} USDT</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="elb-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">FUTURES margin</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{fut_margin:,.2f} USDT</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="elb-card">', unsafe_allow_html=True)
        color = "#22c55e" if pnl_total_tp >= 0 else "#ef4444"
        sign = "+" if pnl_total_tp >= 0 else ""
        st.markdown('<div class="metric-label">P&L total TP</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value" style="color:{color};">{sign}{pnl_total_tp:,.2f} USDT</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ======================== TABELA TP ========================
    st.markdown("### 📘 Skenari TP – rënie (−%) dhe rikthim në 0%")

    tp_row = {
        "Investimi total": round(investimi_total, 2),
        "SPOT %": spot_pct,
        "FUTURES %": futures_pct,
        "Leverage": leverage,
        "TP rënia (%)": tp_down_percent,
        "Fitimi FUTURES në −TP%": round(fut_profit_tp, 2),
        "Humbja SPOT në −TP%": round(spot_loss_tp, 2),
        "Fitimi final në 0%": round(pnl_total_tp, 2),
        "Totali final në 0%": round(total_final_tp, 2),
    }

    if coins_total_tp is not None:
        tp_row["Coin-a fillestarë"] = round(coins_initial, 2)
        tp_row["Coin nga fitimi i futures"] = round(coins_from_tp, 2)
        tp_row["Coin total në 0%"] = round(coins_total_tp, 2)

    tp_df = pd.DataFrame([tp_row])
    st.dataframe(tp_df, use_container_width=True)

    # ======================== TABELA SL ========================
    st.markdown("### 📕 Skenari SL – ngritje (+%)")

    sl_df = pd.DataFrame([{
        "Investimi total": round(investimi_total, 2),
        "SPOT %": spot_pct,
        "FUTURES %": futures_pct,
        "Leverage": leverage,
        "SL ngritja (%)": sl_up_percent,
        "Fitimi SPOT në +SL%": round(spot_profit_sl, 2),
        "Humbja FUTURES në +SL%": round(fut_loss_sl, 2),
        "P&L total në +SL%": round(pnl_sl, 2),
        "Kapitali final në +SL%": round(total_sl, 2),
    }])

    st.dataframe(sl_df, use_container_width=True)

else:
    st.info("👉 Shkruaj një shumë > 0 te 'Investimi total' që të shohësh rezultatet.")