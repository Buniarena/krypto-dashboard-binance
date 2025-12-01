import streamlit as st
import pandas as pd

# ======================== KONFIGURIMI BAZË ========================
st.set_page_config(
    page_title="ElBuni PRO Shields",
    page_icon="🛡",
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
    font-size: 32px;
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

# ======================== HEADER ========================
st.markdown("""
<div class="elb-card">
  <div class="elb-title">🛡 ElBuni PRO Shields</div>
  <div style="font-size:15px;color:#cbd5f5;">
    Laborator për mbrojtjen profesionale të kapitalit: TRI-HEDGE, Wave Shield dhe Auto-Adjust SL.
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# ======================== PRICE HELPER – LLOGARIT ÇMIMIN NGA % ========================
st.markdown("### 📐 Price Helper – Llogarit çmimin nga përqindjet që shkruan vet")

col_price_1, col_price_2 = st.columns(2)
with col_price_1:
    entry_price = st.number_input(
        "💲 Çmimi hyrës (entry)",
        min_value=0.0,
        value=0.00000457,
        format="%.10f",
        key="helper_entry"
    )
with col_price_2:
    pct_text = st.text_input(
        "📊 Përqindjet (shkruaj vet, p.sh. -2, 1.5, 3, -5)",
        value="-2, 1, 2, 3, 4, 5",
        key="helper_pcts"
    )

if entry_price > 0 and pct_text.strip() != "":
    percents = []
    for part in pct_text.replace(";", ",").split(","):
        part = part.strip()
        if part == "":
            continue
        try:
            percents.append(float(part))
        except ValueError:
            pass  # injoro input jo valid

    if percents:
        rows = []
        for p in percents:
            new_price = entry_price * (1 + p/100.0)
            rows.append({
                "Lëvizja (%)": p,
                "Çmimi i ri": float(f"{new_price:.10f}")
            })

        df_price = pd.DataFrame(rows).sort_values("Lëvizja (%)")
        st.markdown("#### 📊 Tabela e çmimeve sipas përqindjeve")
        st.dataframe(df_price, use_container_width=True)
    else:
        st.info("Shkruaj përqindje valide, p.sh. -2, 1, 3.5, -5")

st.markdown("---")

# ======================== ZGJEDH SHIELD ========================
mode = st.selectbox(
    "Zgjidh shield-in:",
    ["ElBuni TRI-HEDGE", "ElBuni Wave Shield", "ElBuni Auto-Adjust PRO"]
)

# =========================================================
# 1) TRI-HEDGE – SPOT + SHORT + LONG
# =========================================================
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
        tri_short_pct = st.slider(
            "📉 SHORT futures (%)",
            0,
            100 - tri_spot_pct,
            20,
            key="tri_short_pct"
        )
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
        # Ndarja e kapitalit
        spot_cap_tri = tri_cap * tri_spot_pct / 100.0
        short_margin_tri = tri_cap * tri_short_pct / 100.0
        long_margin_tri = tri_cap * tri_long_pct / 100.0

        short_notional = short_margin_tri * short_leverage
        long_notional = long_margin_tri * long_leverage

        d = move_down / 100.0
        u = move_up / 100.0

        # ---- Skenari rënie (−%) ----
        spot_loss_down = spot_cap_tri * d
        short_profit_down = short_notional * d
        long_loss_down = long_notional * d

        pnl_down = -spot_loss_down + short_profit_down - long_loss_down
        total_down = tri_cap + pnl_down

        # ---- Skenari ngritje (+%) ----
        spot_profit_up = spot_cap_tri * u
        short_loss_up = short_notional * u
        long_profit_up = long_notional * u

        pnl_up = spot_profit_up - short_loss_up + long_profit_up
        total_up = tri_cap + pnl_up

        tri_df = pd.DataFrame([{
            "Kapitali total": tri_cap,
            "SPOT (USDT)": spot_cap_tri,
            "SHORT margin": short_margin_tri,
            "LONG margin": long_margin_tri,
            "SHORT notional": short_notional,
            "LONG notional": long_notional,
            "P&L në rënie (USDT)": pnl_down,
            "Kapitali në rënie": total_down,
            "P&L në ngritje (USDT)": pnl_up,
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
- Në rënie → SHORT të mbron, SPOT humbet, LONG humb pak → P&L afër zeros.
- Në ngritje → SPOT + LONG fitojnë, SHORT humb → P&L priret të jetë në plus.

E mirë kur nuk je i sigurt në drejtimin e tregut, por do të ulësh rrezikun total.
""")


# =========================================================
# 2) WAVE SHIELD – VALË lart/poshtë me TP të vegjël
# =========================================================
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

        tp_fraction = wave_tp_each / 100.0

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
            "Fitim total/cikël": total_profit_cycle
        }])

        st.markdown("### 📊 Rezultatet e një cikli Wave Shield")
        st.dataframe(wave_df, use_container_width=True)

        colW1, colW2 = st.columns(2)
        with colW1:
            st.metric("Fitim total/cikël", f"{total_profit_cycle:,.2f} USDT")
        with colW2:
            perc = (total_profit_cycle / wave_cap * 100.0) if wave_cap > 0 else 0.0
            st.metric("Fitim % mbi kapitalin", f"{perc:.2f} %")

        st.markdown("""
**🧠 Si funksionon Wave Shield:**
- 50% e kapitalit punon në valët poshtë (TP short të vegjël).
- 50% në valët lart (TP long të vegjël).
- Sa herë çmimi bën zig-zag, ti mbyll TP të vogla dhe mbledh fitime,
  pa pasur nevojë të parashikosh bull ose bear afatgjatë.
""")


# =========================================================
# 3) AUTO-ADJUST PRO – Trailing SL inteligjent
# =========================================================
elif mode == "ElBuni Auto-Adjust PRO":
    st.markdown("### 🤖 ElBuni Auto-Adjust PRO – Stop Loss inteligjent")

    st.markdown("""
Ky modul simulon një **trailing SL** që afrohet sa herë çmimi lëviz në favorin tënd.
Mban nën kontroll humbjen maksimale dhe fillon të “bllokojë” fitimin.
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

    if auto_cap > 0 and initial_sl_dist > 0:
        initial_risk_usdt = auto_cap * risk_pct / 100.0

        if move_up_now <= trail_trigger:
            current_sl_dist = initial_sl_dist
        else:
            extra_move = move_up_now - trail_trigger
            current_sl_dist = max(0.0, initial_sl_dist - extra_move * trail_step)

        current_max_loss_pct = risk_pct * (current_sl_dist / initial_sl_dist)
        current_max_loss_usdt = auto_cap * current_max_loss_pct / 100.0

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
- Në fillim pranon një rrezik të kufizuar (p.sh. 2% e kapitalit).
- Kur çmimi ecën në drejtimin tënd, SL afrohet gjithnjë e më shumë.
- Sa më shumë lëviz çmimi, aq më pak humbje maksimale lejon, dhe një pjesë e fitimit bëhet “e siguruar”.

Kështu pozicioni yt nuk rri i ekspozuar pa kontroll – është gjithmonë nën mbrojtje dinamike.
""")

# ===================== FUND – SQARIM I SHKURTËR ========================
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div style="font-size:14px;color:#9ca3af;">
ElBuni PRO Shields punon si shtesë mbi ElBuni Strategy / BP:
TRI-HEDGE për drejtim të pasigurt, Wave Shield për treg me valë dhe Auto-Adjust PRO për SL inteligjent.
Price Helper sipër të jep shpejt çmimet për TP/SL nga çdo përqindje që shkruan vet.
</div>
""", unsafe_allow_html=True)