import streamlit as st
import pandas as pd
from PIL import Image
import os  # për ruajtjen e logos në disk

# ======================== KONFIGURIMI BAZË ========================
st.set_page_config(
    page_title="ElBuni Strategy PRO – TP & SL + Manual + GRID + Shields + BP",
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
    except Exception:
        logo_to_show = None

# ======================== HEADER ME LOGO ========================
st.markdown("")

if logo_to_show is not None:
    st.image(logo_to_show, use_column_width=False, width=420)
else:
    st.markdown("### 💹 ElBuni Strategy PRO")

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# ======================== TABS ========================
tab_calc, tab_manual, tab_grid, tab_shields, tab_bp = st.tabs(
    [
        "🧮 Kalkulatori",
        "📘 Manuali i Strategjisë",
        "🧱 ElBuni GRID",
        "🛡 ElBuni PRO Shields",
        "🧲 ElBuni BP (BTC + PEPE)"
    ]
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
        format="%.12f"
    )

    st.markdown("---")

    # ======================== ÇMIMET TP & SL ========================
    if price_entry > 0:
        tp_price = price_entry * (1 - tp_down_percent / 100)
        sl_price = price_entry * (1 + sl_up_percent / 100)

        st.markdown("### 💲 Çmimet për Binance")

        ct1, ct2 = st.columns(2)

        with ct1:
            st.markdown('<div class="elb-card">📉 Çmimi TP</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{tp_price:.12f}</div>', unsafe_allow_html=True)

        with ct2:
            st.markdown('<div class="elb-card">📈 Çmimi SL</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{sl_price:.12f}</div>', unsafe_allow_html=True)

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
        format="%.12f",
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
            buy_price = entry_grid * (1 - (step_percent / 100) * i)
            tp_price = buy_price * (1 + tp_percent / 100)

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

# ======================== TAB 4: ELBUNI PRO SHIELDS ========================
with tab_shields:
    st.markdown("## 🛡 ElBuni PRO Shields – Mbrojtje Profesionale e Investimit")

    mode = st.selectbox(
        "Zgjidh shield-in:",
        ["ElBuni TRI-HEDGE", "ElBuni Wave Shield", "ElBuni Auto-Adjust PRO"]
    )

    # ---------- 1) TRI-HEDGE ----------
    if mode == "ElBuni TRI-HEDGE":
        st.markdown("### 🥇 ElBuni TRI-HEDGE – SPOT + SHORT + LONG")

        colA, colB = st.columns(2)
        with colA:
            tri_cap = st.number_input(
                "💰 Kapitali total (USDT)",
                min_value=0.0,
                value=5000.0,
                step=100.0,
                key="tri_cap"
            )
        with colB:
            short_leverage = st.number_input(
                "⚙️ Leverage SHORT (x)",
                min_value=1.0,
                max_value=10.0,
                value=2.0,
                step=0.5,
                key="tri_short_lev"
            )

        colP1, colP2, colP3 = st.columns(3)
        with colP1:
            tri_spot_pct = st.slider("📊 SPOT (%)", 0, 100, 60, key="tri_spot_pct")
        with colP2:
            tri_short_pct = st.slider("📉 SHORT futures (%)", 0, 100 - tri_spot_pct, 20, key="tri_short_pct")
        with colP3:
            tri_long_pct = 100 - tri_spot_pct - tri_short_pct
            st.markdown(f"**📈 LONG futures (%) = {tri_long_pct}%**")

        colMv = st.columns(2)
        with colMv[0]:
            move_down = st.number_input(
                "📉 Skenari rënie (−%)",
                min_value=0.1,
                max_value=80.0,
                value=5.0,
                step=0.1,
                key="tri_down"
            )
        with colMv[1]:
            move_up = st.number_input(
                "📈 Skenari ngritje (+%)",
                min_value=0.1,
                max_value=80.0,
                value=5.0,
                step=0.1,
                key="tri_up"
            )

        long_leverage = st.number_input(
            "⚙️ Leverage LONG (x)",
            min_value=1.0,
            max_value=10.0,
            value=1.5,
            step=0.5,
            key="tri_long_lev"
        )

        st.markdown("---")

        if tri_cap > 0:
            spot_cap_tri = tri_cap * tri_spot_pct / 100
            short_margin_tri = tri_cap * tri_short_pct / 100
            long_margin_tri = tri_cap * tri_long_pct / 100

            short_notional = short_margin_tri * short_leverage
            long_notional = long_margin_tri * long_leverage

            d = move_down / 100
            u = move_up / 100

            # Skenari rënie
            spot_loss_down = spot_cap_tri * d
            short_profit_down = short_notional * d
            long_loss_down = long_notional * d

            pnl_down = -spot_loss_down + short_profit_down - long_loss_down
            total_down = tri_cap + pnl_down

            # Skenari ngritje
            spot_profit_up = spot_cap_tri * u
            short_loss_up = short_notional * u
            long_profit_up = long_notional * u

            pnl_up = spot_profit_up - short_loss_up + long_profit_up
            total_up = tri_cap + pnl_up

            tri_df = pd.DataFrame([{
                "Kapitali": tri_cap,
                "SPOT (USDT)": spot_cap_tri,
                "SHORT margin": short_margin_tri,
                "LONG margin": long_margin_tri,
                "SHORT notional": short_notional,
                "LONG notional": long_notional,
                "P&L në rënie (−%)": pnl_down,
                "Kapitali në rënie": total_down,
                "P&L në ngritje (+%)": pnl_up,
                "Kapitali në ngritje": total_up
            }])

            st.markdown("### 📊 Rezultatet TRI-HEDGE")
            st.dataframe(tri_df, use_container_width=True)

            colR1, colR2 = st.columns(2)
            with colR1:
                st.metric("P&L në rënie", f"{pnl_down:,.2f} USDT")
            with colR2:
                st.metric("P&L në ngritje", f"{pnl_up:,.2f} USDT")

            st.markdown("""
**🧠 Ideja e TRI-HEDGE:**
- Në rënie → SHORT të mbron, LONG humb pak → P&L afër zeros.  
- Në ngritje → SPOT + LONG fitojnë, SHORT humb pak → P&L në plus.  
Ky kombinim ul shumë rrezikun e drejtimit të gabuar të tregut.
""")

    # ---------- 2) WAVE SHIELD ----------
    elif mode == "ElBuni Wave Shield":
        st.markdown("### 🌊 ElBuni Wave Shield – Mbrojtje me Valë")

        colA, colB = st.columns(2)
        with colA:
            wave_cap = st.number_input(
                "💰 Kapitali total për Wave Shield (USDT)",
                min_value=0.0,
                value=2000.0,
                step=50.0,
                key="wave_cap"
            )
            wave_short_levels = st.number_input(
                "📉 Numri i TP Short (valët poshtë)",
                min_value=1,
                max_value=10,
                value=3,
                key="wave_short_levels"
            )
        with colB:
            wave_long_levels = st.number_input(
                "📈 Numri i TP Long (valët lart)",
                min_value=1,
                max_value=10,
                value=2,
                key="wave_long_levels"
            )
            wave_tp_each = st.number_input(
                "🎯 TP për çdo valë (+/− %)",
                min_value=0.1,
                max_value=20.0,
                value=1.5,
                step=0.1,
                key="wave_tp_each"
            )

        st.markdown("---")

        if wave_cap > 0:
            cap_short = wave_cap * 0.5
            cap_long = wave_cap * 0.5

            per_short = cap_short / wave_short_levels
            per_long = cap_long / wave_long_levels

            tp_fraction = wave_tp_each / 100

            profit_per_short = per_short * tp_fraction
            profit_per_long = per_long * tp_fraction

            total_profit_short = profit_per_short * wave_short_levels
            total_profit_long = profit_per_long * wave_long_levels
            total_profit_cycle = total_profit_short + total_profit_long

            wave_df = pd.DataFrame([{
                "Kapital total": wave_cap,
                "Kapital për SHORT-valë": cap_short,
                "Kapital për LONG-valë": cap_long,
                "Fitim total SHORT-valë": total_profit_short,
                "Fitim total LONG-valë": total_profit_long,
                "Fitim total cikël": total_profit_cycle
            }])

            st.markdown("### 📊 Rezultatet e një cikli Wave Shield")
            st.dataframe(wave_df, use_container_width=True)

            colW1, colW2 = st.columns(2)
            with colW1:
                st.metric("Fitim total/cikël (USDT)", f"{total_profit_cycle:,.2f}")
            with colW2:
                st.metric("Fitim % mbi kapitalin", f"{(total_profit_cycle / wave_cap * 100 if wave_cap > 0 else 0):.2f}%")

            st.markdown("""
**🧠 Si funksionon Wave Shield:**
- Gjysma e kapitalit punon në valët poshtë (TP short të vegjël).  
- Gjysma tjetër punon në valët lart (TP long të vegjël).  
- Sa herë çmimi bën zig-zag, ti mbyll TP të vogla dhe mbledh fitime pa pasur nevojë të parashikosh bull/bear afatgjatë.
""")

    # ---------- 3) AUTO-ADJUST PRO ----------
    elif mode == "ElBuni Auto-Adjust PRO":
        st.markdown("### 🤖 ElBuni Auto-Adjust PRO – Stop Loss inteligjent")

        st.markdown("""
Ky modul tregon si lëviz automatikisht rreziku i humbjes kur çmimi lëviz në favorin tënd.
Mendoje si një **SL që ngjitet lart** sa herë që çmimi ecën në drejtimin e duhur.
""")

        colA, colB = st.columns(2)
        with colA:
            auto_cap = st.number_input(
                "💰 Kapitali i pozicionit (USDT)",
                min_value=0.0,
                value=1000.0,
                step=50.0,
                key="auto_cap"
            )
            risk_pct = st.number_input(
                "⚠️ Rreziku maksimal fillestar (% kapitalit)",
                min_value=0.1,
                max_value=20.0,
                value=2.0,
                step=0.1,
                key="auto_risk"
            )
            initial_sl_dist = st.number_input(
                "📍 Distanca fillestare SL nga entry (+/− %)",
                min_value=0.1,
                max_value=20.0,
                value=4.0,
                step=0.1,
                key="auto_sl_dist"
            )
        with colB:
            trail_trigger = st.number_input(
                "🚦 Aktivizo trailing kur çmimi lëviz (+%)",
                min_value=0.1,
                max_value=20.0,
                value=2.0,
                step=0.1,
                key="auto_trigger"
            )
            trail_step = st.number_input(
                "📈 Sa % afrohet SL për çdo +1% shtesë",
                min_value=0.1,
                max_value=10.0,
                value=1.0,
                step=0.1,
                key="auto_trail"
            )
            move_up_now = st.number_input(
                "📊 Sa % ka lëvizur çmimi në favorin tënd (+%)",
                min_value=0.0,
                max_value=200.0,
                value=3.0,
                step=0.1,
                key="auto_move"
            )

        st.markdown("---")

        if auto_cap > 0:
            initial_risk_usdt = auto_cap * risk_pct / 100

            if move_up_now <= trail_trigger:
                current_sl_dist = initial_sl_dist
            else:
                extra_move = move_up_now - trail_trigger
                current_sl_dist = max(0.0, initial_sl_dist - extra_move * (trail_step / 1.0))

            if initial_sl_dist > 0:
                current_max_loss_pct = min(risk_pct, risk_pct * current_sl_dist / initial_sl_dist)
            else:
                current_max_loss_pct = 0.0

            current_max_loss_usdt = auto_cap * current_max_loss_pct / 100
            locked_profit = max(0.0, initial_risk_usdt - current_max_loss_usdt)

            auto_df = pd.DataFrame([{
                "Kapital i pozicionit": auto_cap,
                "Rrezik fillestar %": risk_pct,
                "Rrezik fillestar (USDT)": initial_risk_usdt,
                "Distanca fillestare SL (%)": initial_sl_dist,
                "Lëvizja aktuale e çmimit (+%)": move_up_now,
                "Distanca aktuale SL (%)": current_sl_dist,
                "Humbja maksimale aktuale (USDT)": current_max_loss_usdt,
                "Fitim i 'bllokuar' (USDT)": locked_profit
            }])

            st.markdown("### 📊 Trailing SL – gjendja aktuale")
            st.dataframe(auto_df, use_container_width=True)

            colM1, colM2, colM3 = st.columns(3)
            with colM1:
                st.metric("Rreziku fillestar (USDT)", f"{initial_risk_usdt:,.2f}")
            with colM2:
                st.metric("Rreziku maksimal aktual", f"{current_max_loss_usdt:,.2f} USDT")
            with colM3:
                st.metric("Fitim i mbrojtur (locked)", f"{locked_profit:,.2f} USDT")

            st.markdown("""
**🧠 Ideja e Auto-Adjust PRO:**
- Në fillim pranon një rrezik maksimal (p.sh. 2% e kapitalit).  
- Kur çmimi lëviz në favorin tënd, SL afrohet automatikisht.  
- Sa më shumë ecën çmimi, aq më shumë ulet humbja maksimale → dhe mund të bllokohet fitimi.  

Kështu pozicioni yt nuk rri i hapur “pa kontrolle”, por ndiqet nga një SL inteligjent që mbron fitimin.
""")

# ======================== TAB 5: ELBUNI BP (BTC + PEPE) ========================
with tab_bp:
    st.markdown("## 🧲 ElBuni BP – BTC Short + PEPE Spot (Inverse Hedge)")

    st.markdown("""
**ElBuni BP** = kombinim **BTC SHORT (futures)** + **PEPE SPOT**.  
Ideja:  
- kur BTC bie → fiton nga short-i + PEPE mund të bjerë më pak ose të rritet  
- kur BTC rritet → PEPE shpesh nuk ndjek 1:1 lëvizjen e BTC-së  

Këtu mund të testosh skenarë të ndryshëm se si reagojnë BTC dhe PEPE.
""")

    st.markdown("---")

    colA, colB, colC = st.columns(3)

    with colA:
        bp_cap = st.number_input(
            "💰 Kapitali total për ElBuni BP (USDT)",
            min_value=0.0,
            value=5000.0,
            step=100.0,
            key="bp_cap"
        )

    with colB:
        bp_spot_pepe_pct = st.slider(
            "🐸 PEPE SPOT (%)",
            0, 100, 60,
            key="bp_spot_pepe_pct"
        )

    with colC:
        bp_lev_btc = st.number_input(
            "⚙️ Leverage BTC SHORT (x)",
            min_value=1.0,
            max_value=10.0,
            value=2.0,
            step=0.5,
            key="bp_lev_btc"
        )

    bp_fut_btc_pct = 100 - bp_spot_pepe_pct
    st.markdown(f"**₿ BTC SHORT futures (%) = {bp_fut_btc_pct}%**")

    st.markdown("---")

    colMv1, colMv2 = st.columns(2)
    with colMv1:
        btc_down_pct = st.number_input(
            "📉 Rënia e BTC (−%) – skenari 1",
            min_value=0.1,
            max_value=80.0,
            value=5.0,
            step=0.1,
            key="bp_btc_down"
        )
        pepe_react_down = st.number_input(
            "🐸 Lëvizja e PEPE kur BTC bie (±%)",
            min_value=-100.0,
            max_value=100.0,
            value=2.0,
            step=0.1,
            key="bp_pepe_down"
        )
    with colMv2:
        btc_up_pct = st.number_input(
            "📈 Ngritja e BTC (+%) – skenari 2",
            min_value=0.1,
            max_value=80.0,
            value=5.0,
            step=0.1,
            key="bp_btc_up"
        )
        pepe_react_up = st.number_input(
            "🐸 Lëvizja e PEPE kur BTC ngrihet (±%)",
            min_value=-100.0,
            max_value=100.0,
            value=-1.0,
            step=0.1,
            key="bp_pepe_up"
        )

    st.markdown("---")

    price_pepe_entry = st.number_input(
        "💲 Çmimi hyrës i PEPE (opsionale, për coin-at)",
        min_value=0.0,
        value=0.00000457,
        format="%.12f",
        key="bp_pepe_entry"
    )

    if bp_cap > 0:
        cap_spot_pepe = bp_cap * bp_spot_pepe_pct / 100
        cap_fut_btc_margin = bp_cap * bp_fut_btc_pct / 100
        notional_btc_short = cap_fut_btc_margin * bp_lev_btc

        # ===== Skenari 1: BTC bie =====
        d_btc = btc_down_pct / 100.0
        d_pepe = pepe_react_down / 100.0

        btc_profit_down = notional_btc_short * d_btc
        pepe_pnl_down = cap_spot_pepe * d_pepe

        pnl_total_down = btc_profit_down + pepe_pnl_down
        cap_total_down = bp_cap + pnl_total_down

        # ===== Skenari 2: BTC ngrihet =====
        u_btc = btc_up_pct / 100.0
        u_pepe = pepe_react_up / 100.0

        btc_loss_up = notional_btc_short * u_btc * (-1)
        pepe_pnl_up = cap_spot_pepe * u_pepe

        pnl_total_up = btc_loss_up + pepe_pnl_up
        cap_total_up = bp_cap + pnl_total_up

        # opcional: coin-a PEPE
        coins_pepe_initial = coins_pepe_down = coins_pepe_up = None
        if price_pepe_entry > 0:
            coins_pepe_initial = cap_spot_pepe / price_pepe_entry

            price_pepe_down = price_pepe_entry * (1 + d_pepe)
            price_pepe_up = price_pepe_entry * (1 + u_pepe)
            if price_pepe_down > 0:
                coins_pepe_down = cap_spot_pepe * (1 + d_pepe) / price_pepe_down
            if price_pepe_up > 0:
                coins_pepe_up = cap_spot_pepe * (1 + u_pepe) / price_pepe_up

        # ===== Tabela rezultatit =====
        bp_df = pd.DataFrame([
            {
                "Skenari": "BTC bie",
                "BTC lëvizja (%)": -btc_down_pct,
                "PEPE lëvizja (%)": pepe_react_down,
                "Kapital total (USDT)": cap_total_down,
                "P&L total (USDT)": pnl_total_down
            },
            {
                "Skenari": "BTC ngrihet",
                "BTC lëvizja (%)": btc_up_pct,
                "PEPE lëvizja (%)": pepe_react_up,
                "Kapital total (USDT)": cap_total_up,
                "P&L total (USDT)": pnl_total_up
            }
        ])

        st.markdown("### 📊 Rezultatet ElBuni BP – BTC + PEPE")
        st.dataframe(bp_df, use_container_width=True)

        colBP1, colBP2 = st.columns(2)
        with colBP1:
            st.metric("P&L kur BTC bie", f"{pnl_total_down:,.2f} USDT")
        with colBP2:
            st.metric("P&L kur BTC ngrihet", f"{pnl_total_up:,.2f} USDT")

        if coins_pepe_initial is not None:
            st.markdown("### 🐸 PEPE – Coin-at në skenarë")

            st.markdown(f"""
- Coin fillestarë PEPE: **{coins_pepe_initial:,.2f}**  
- Coin efektivë në skenarin BTC bie: **{coins_pepe_down if coins_pepe_down is not None else coins_pepe_initial:,.2f}**  
- Coin efektivë në skenarin BTC ngrihet: **{coins_pepe_up if coins_pepe_up is not None else coins_pepe_initial:,.2f}**
""")

        st.markdown("""
**🧠 Interpretimi i ElBuni BP:**
- Zgjedh një raport PEPE SPOT / BTC SHORT.  
- Cakton sa lëviz BTC dhe sa pritet të reagojë PEPE kur BTC bie / ngrihet.  
- Shikon menjëherë nëse kjo lidhje të jep **hedging të fortë** apo jo.  

Kështu mund të gjesh konfigurimin ideal ku:
- në rënie të BTC → fitimi nga short + reagimi i PEPE të japin P&L pozitiv  
- në ngritje të BTC → nuk digjesh fort sepse PEPE nuk ndjek 1:1 lëvizjen e BTC-së.  
""")

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

    Me shtesën <b>ElBuni BP (BTC + PEPE)</b> ti ke edhe një modul special për hedging midis coinit kryesor (BTC) dhe një meme-coini si PEPE,
    ku mund të shohësh direkt se si ndikojnë rëniet dhe ngritjet e BTC-së te portofoli yt i kombinuar.
  </div>
</div>
""", unsafe_allow_html=True)