import streamlit as st
import pandas as pd

# ======================== KONFIGURIMI BAZË ========================
st.set_page_config(
    page_title="ElBuni Strategy PRO – Hedging Calculator",
    page_icon="💹",
    layout="wide"
)

# ======================== STILIMI (CSS) ========================
st.markdown("""
<style>
/* Background */
.main {
    background: radial-gradient(circle at top left, #03131f, #020814 50%, #000000 100%);
    color: #f5f5f5;
    font-family: "Segoe UI", system-ui;
}

/* Cards */
.elb-card {
    background: rgba(10, 20, 40, 0.9);
    border-radius: 18px;
    padding: 18px 24px;
    border: 1px solid rgba(0, 255, 204, 0.18);
    box-shadow: 0 0 25px rgba(0, 0, 0, 0.5);
}

/* Header title */
.elb-title {
    font-size: 38px;
    font-weight: 700;
    color: #00f5d4;
    text-shadow: 0 0 14px rgba(0, 245, 212, 0.6);
    margin-bottom: 6px;
}

/* Subtitle */
.elb-subtitle {
    font-size: 15px;
    color: #cbd5f5;
}

/* Section titles */
h2, h3 {
    color: #e0f7ff !important;
}

/* Metrics */
.metric-label {
    font-size: 13px;
    color: #9ca3af;
}
.metric-value {
    font-size: 24px;
    font-weight: 700;
}

/* Dataframe cleanup */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #020617 40%, #020617);
    border-right: 1px solid rgba(148, 163, 184, 0.3);
}

/* Buttons */
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

/* Slider label color */
div[role="slider"] + div {
    color: #e5e7eb !important;
}
</style>
""", unsafe_allow_html=True)

# ======================== SIDEBAR – PRESETS ========================
with st.sidebar:
    st.markdown("### ⚙️ ElBuni Presets")
    st.caption("Zgjidh shpejt konfigurimet më të përdorura.")

    preset = st.selectbox(
        "Zgjidh preset:",
        [
            "Custom",
            "20,000 USDT – 70/30 – x2 – (-4%)",
            "10,000 USDT – 70/30 – x3 – (-3%)",
            "50,000 USDT – 60/40 – x3 – (-5%)"
        ]
    )

    default_invest = 20000.0
    default_spot_pct = 70
    default_lev = 2.0
    default_drop = 4.0

    if preset == "20,000 USDT – 70/30 – x2 – (-4%)":
        default_invest = 20000.0
        default_spot_pct = 70
        default_lev = 2.0
        default_drop = 4.0
    elif preset == "10,000 USDT – 70/30 – x3 – (-3%)":
        default_invest = 10000.0
        default_spot_pct = 70
        default_lev = 3.0
        default_drop = 3.0
    elif preset == "50,000 USDT – 60/40 – x3 – (-5%)":
        default_invest = 50000.0
        default_spot_pct = 60
        default_lev = 3.0
        default_drop = 5.0

    st.markdown("---")
    st.caption("💡 **Tip:** Mbaj futures rreth 30% të kapitalit për hedging më të sigurt.")

# ======================== HEADER ========================
st.markdown(
    """
    <div class="elb-card">
        <div class="elb-title">💹 ElBuni Strategy PRO</div>
        <div class="elb-subtitle">
            Hedging kalkulator profesional për kombinimin <b>SPOT + FUTURES SHORT</b>.<br>
            Futesh me një skenar, del me numra: fitimi i futures, humbja e spot, P&L në rënie dhe fitimi final kur çmimi kthehet në <b>0%</b>.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("")

# ======================== INPUTET KRYESORE ========================
st.markdown("### 📥 Parametrat kryesorë të strategjisë")

colA, colB = st.columns(2)

with colA:
    investimi_total = st.number_input(
        "💰 Investimi total (USDT)",
        min_value=0.0,
        value=default_invest,
        step=100.0
    )
    spot_pct = st.slider("📊 Përqindja në SPOT (%)", 0, 100, default_spot_pct)
    leverage = st.number_input(
        "⚙️ Leverage për FUTURES (x)",
        min_value=1.0,
        value=default_lev,
        step=0.5
    )

with colB:
    futures_pct = 100 - spot_pct
    st.markdown(f"**📉 Përqindja në FUTURES:** `{futures_pct}%`")
    drop_percent = st.number_input(
        "📉 Rënia ku mbyll SHORT-in (–%)",
        min_value=0.1,
        max_value=80.0,
        value=default_drop,
        step=0.1
    )
    price_entry = st.number_input(
        "💲 Çmimi hyrës i coinit (opsionale – për coin-at)",
        min_value=0.0,
        value=0.00000457,
        format="%.12f"
    )

st.markdown("---")

# ======================== LLOGARITJET ========================
if investimi_total > 0:
    d = drop_percent / 100.0

    # Kapitali në spot & futures
    spot_cap = investimi_total * spot_pct / 100.0      # para në SPOT
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

    # ======================== KARTAT E SHPEJTA (INSIGHT) ========================
    st.markdown("### 📊 Insight i shpejtë i skenarit")

    c1, c2, c3, c4 = st.columns(4)

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
        st.markdown(f'<div class="metric-label">Fitimi FUTURES në -{drop_percent:.1f}%</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">+{fut_profit_drop:,.2f} USDT</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="elb-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Fitimi total në 0%</div>', unsafe_allow_html=True)
        color_pnl = "#22c55e" if total_pnl_final >= 0 else "#ef4444"
        sign = "+" if total_pnl_final >= 0 else ""
        st.markdown(
            f'<div class="metric-value" style="color:{color_pnl};">{sign}{total_pnl_final:,.2f} USDT</div>',
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("")

    # ======================== TABELA E DETAJUAR ========================
    st.markdown("### 🧮 Detajet e plota të skenarit ElBuni")

    calc_rows = [{
        "Investimi total (USDT)": round(investimi_total, 2),
        "SPOT fillestar (USDT)": round(spot_cap, 2),
        "FUTURES margin (USDT)": round(fut_margin, 2),
        "Leverage FUTURES (x)": leverage,
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

    st.dataframe(calc_df, use_container_width=True)

    # ======================== PËRMBLEDHJE ME TEKST ========================
    st.markdown("### 📝 Përmbledhje analitike")

    sign_drop = "+" if total_pnl_drop >= 0 else ""
    sign_final = "+" if total_pnl_final >= 0 else ""

    st.markdown(f"""
**Rënia dhe mbyllja e short-it**

- Në rënien **-{drop_percent:.1f}%**:
  - SPOT humb: **{spot_loss_drop:,.2f} USDT**
  - FUTURES fiton: **{fut_profit_drop:,.2f} USDT**
  - P&L total në momentin e mbylljes së short-it: **{sign_drop}{total_pnl_drop:,.2f} USDT**

**Hedhja e fitimit të futures në spot & rikthimi në 0%**

- Fitimi i futures **hidhet në SPOT** në çmimin e rënies.
- Kur çmimi kthehet sërish në **0%**:
  - Fitimi total final i strategjisë: **{sign_final}{total_pnl_final:,.2f} USDT**
  - Kapitali total bëhet: **{total_final:,.2f} USDT** (nga {investimi_total:,.2f} USDT)
""")

    if coins_total is not None:
        st.markdown(f"""
**Niveli i coinit**

- Coin-a fillestarë: **{coins_initial:,.2f}**
- Coin-a të marrë nga fitimi i futures: **{coins_from_profit:,.2f}**
- Totali i coin-it kur çmimi kthehet në 0%: **{coins_total:,.2f}**
""")

else:
    st.info("👉 Shkruaj një shumë > 0 në 'Investimi total' për të parë llogaritjet e ElBuni Strategy PRO.")