import streamlit as st
import pandas as pd

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

# ======================== HEADER ========================
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
            value=2.0,   # mund ta ndryshosh si të duash, manuali është shembull me 2x
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
    tp_price = None
    sl_price = None

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

        spot_loss_tp = spot_cap * d_tp             # humbja në SPOT
        fut_profit_tp = fut_notional * d_tp        # fitimi në FUTURES

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
            st.markdown('<div class="metric-label">P&L total TP (−%)</div>', unsafe_allow_html=True)
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

        # ======================== PËRMBLEDHJA NË FUND ========================
        st.markdown("### 📝 Përmbledhje e strategjisë për këtë konfigurim")

        sign_tp = "+" if pnl_total_tp >= 0 else ""
        sign_sl = "+" if pnl_sl >= 0 else ""

        st.markdown(f"""
**📌 Çfarë ke futur:**
- Investimi total: **{investimi_total:,.2f} USDT**
- SPOT: **{spot_cap:,.2f} USDT** ({spot_pct}%)
- FUTURES margin: **{fut_margin:,.2f} USDT** ({futures_pct}%)
- Leverage i FUTURES: **x{leverage}**

**🎯 Skenari TP (rënia −{tp_down_percent:.1f}% dhe rikthim në 0%)**
- Humbja në SPOT në −TP%: **{spot_loss_tp:,.2f} USDT**
- Fitimi në FUTURES në −TP%: **{fut_profit_tp:,.2f} USDT**
- Fitimi total i strategjisë kur çmimi kthehet në 0%: **{sign_tp}{pnl_total_tp:,.2f} USDT**
- Totali i kapitalit në fund (TP + rikthim 0%): **{total_final_tp:,.2f} USDT**

**🛑 Skenari SL (ngritja +{sl_up_percent:.1f}%)**
- Fitimi në SPOT në +SL%: **{spot_profit_sl:,.2f} USDT**
- Humbja në FUTURES në +SL%: **{fut_loss_sl:,.2f} USDT**
- P&L total në momentin e SL: **{sign_sl}{pnl_sl:,.2f} USDT**
- Totali i kapitalit në SL: **{total_sl:,.2f} USDT**

**💎 Në tërësi:**
- Nëse godet **TP** → del me **{sign_tp}{pnl_total_tp:,.2f} USDT** fitim nga kapitali i futur.
- Nëse godet **SL** → del me **{sign_sl}{pnl_sl:,.2f} USDT** fitim/humbje nga kapitali i futur.
""")

    else:
        st.info("👉 Shkruaj një shumë > 0 te 'Investimi total' që të shohësh rezultatet.")

# ======================== TAB 2: MANUALI ========================
with tab_manual:
    st.markdown("## 📘 Manuali i Strategjisë ElBuni (shembull me lev 2x)")

    st.markdown("""
### 1️⃣ Çfarë është ElBuni Strategy?

Strategji hedging ku ti kombinon:

- **SPOT** (blerje normale e coinit)
- **FUTURES SHORT** (short kundër çmimit me leverage)

Qëllimi:
- Të fitosh kur çmimi bie (përmes futures short)
- Të humbasësh sa më pak kur çmimi rritet (sepse ke SPOT)
- Të kesh kontroll mbi **TP (Take Profit)** dhe **SL (Stop Loss)**

---

### 2️⃣ Si ndahet kapitali? (shembull me lev 2x)

Ti zgjedh:

- **SPOT %** → p.sh. 70%
- **FUTURES %** → pjesa tjetër (p.sh. 30%)
- **Leverage** → këtu po marrim shembull **2x**

Shembull konkret:

- Kapitali: **5,000 USDT**
- SPOT 70% → **3,500 USDT**
- FUTURES 30% → **1,500 USDT**
- Leverage **2x** → short total = **3,000 USDT** (1,500 × 2)

Pra:

- 3,500 USDT punojnë si SPOT
- 3,000 USDT pozicion i hapur si SHORT në futures (me margin 1,500 USDT)

---

### 3️⃣ Çfarë ndodh kur çmimi bie (TP)?

Çmimi bie p.sh. **−2%** (TP i short-it):

- SPOT humbet një pjesë (sepse bie çmimi)
- FUTURES SHORT fiton (sepse je short)

Në këtë shembull:

- SPOT 3,500 USDT → bie 2% → humb rreth **70 USDT**
- FUTURES 3,000 USDT short → fiton rreth **60 USDT**

Rezultati:

- Humbje shumë e vogël neto në USDT, por:
- Fiton coin-a shtesë, nëse fitimin e futures e hedh në SPOT në çmimin e rënies.

Pastaj, kur çmimi kthehet prapë në 0%, ti ke:

- më shumë coin në SPOT,
- kapitali total mund të jetë shumë afër shumës fillestare, por me **pozicion më të fortë në sasi coini**.

---

### 4️⃣ Çfarë ndodh kur çmimi rritet (SL)?

Çmimi rritet p.sh. **+6%** (SL):

- SPOT fiton (sepse çmimi rritet)
- FUTURES SHORT humb (sepse short-i shkon kundër teje)

Në shembullin me 70/30 dhe lev 2x:

- SPOT 3,500 USDT → +6% → fiton rreth **210 USDT**
- FUTURES 3,000 USDT short → humb rreth **180 USDT**

Rezultati:

- Fitim neto rreth **+30 USDT**
- Kapitali total është pak **mbi** shumën fillestare

Pra me lev **2x**, strategjia është më e butë:
- në rritje të forta → prapë mund të dalësh pak në fitim ose shumë afër zeros
- në rënie → humbja neto në USDT është e vogël, ndërsa fiton coin-a shtesë kur e hedh fitimin e futures te SPOT.

---

### 5️⃣ Çmimet për Binance (TP & SL)

Kur jep:

- **Çmimin hyrës (entry)**,
- **TP (−%)**,
- **SL (+%)**,

app-i llogarit automatikisht:

- **Çmimin TP** → `entry × (1 − TP%)`
- **Çmimin SL** → `entry × (1 + SL%)`

Këto çmime dalin sipër si numra me 12 decimale, gati për t'u kopjuar direkt në Binance Futures.

---

### 6️⃣ Ku është “edge” i strategjisë me lev 2x?

Me lev **2x**, strategjia për 70/30 ka këtë logjikë:

- Kur çmimi **rritet** → SPOT fiton pak më shumë se humb FUTURES  
  → në skenar SL, shpesh mund të jesh pak në **fitim** ose shumë afër zeros.

- Kur çmimi **bie** → FUTURES fiton, SPOT humbet pak më shumë  
  → në skenar TP, humbja neto në USDT është shumë e vogël, por ti fiton **më shumë coin**.

Pra:

> **Avantazhi** është: ti shton sasinë e coinit në rënie, ndërsa nuk digjesh shumë në rritje të forta, sidomos me lev 2x dhe SL të zgjuar.

Nëse ti e lidh këtë me:

- sinjale teknike (RSI, Bollinger, overbought/oversold),
- filtrat e trendit (mos short në super bull afatgjatë),

atëherë mesatarja afatgjatë të del shumë më e sigurt se një short agresiv me lev 5x–10x.

---

### 7️⃣ Si ta përdorësh në praktikë?

1. Zgjidh coinin në Binance (shpesh meme/alt që lëviz shumë).
2. Në kalkulator (tabi i parë):
   - Vendos **Investimin total**
   - Zgjidh **SPOT %** dhe **FUTURES %**
   - Vendos **Leverage** (p.sh. 2x si në shembull, ose sa do ti)
   - Cakto **TP (−%)** dhe **SL (+%)** sipas riskut tënd
3. Shkruaj **çmimin entry** si në Binance.
4. Kopjo **çmimin TP** dhe **çmimin SL** nga app-i → vendosi tek pozicioni yt në Binance Futures.
5. Shiko përmbledhjen në fund të kalkulatorit:
   - sa ke futur
   - sa del në skenarin TP
   - sa del në skenarin SL
   - sa fitim/humbje ke në total, në USDT dhe në coin.

---

### 8️⃣ Këshilla praktike me lev 2x

- Lev **2x** është shumë më i sigurt se 3x, 5x, 10x – lë vend që tregu të “marrë frymë”.
- Në rritje të forta, strategjia nuk shemb kapitalin, por shpesh nxjerr edhe fitim të vogël.
- Përdore më shumë si **hedging inteligjent**, jo si kumar:
  - hyr nga sinjale të mira, jo rastësisht
  - mos e përdor 24/7 pa filtra
  - testoje fillimisht me shumë më të vogla.

Ky manual është guida jote – kalkulatori në tabin tjetër gjithmonë të tregon saktë numrat për konfigurimin që zgjedh.
""")