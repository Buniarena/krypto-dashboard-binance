import streamlit as st
import math
from datetime import datetime

# ======================== CONFIG ========================
st.set_page_config(
    page_title="ElBuni Strategy PRO",
    page_icon="💹",
    layout="wide"
)

ADMIN_PIN = "3579"

# ======================== SESSION ========================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "page" not in st.session_state:
    st.session_state.page = "Login"

if "journal" not in st.session_state:
    st.session_state.journal = []

# ======================== STIL ========================
st.markdown("""
<style>
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
.hero {
  background: linear-gradient(135deg, rgba(16,185,129,0.18), rgba(255,255,255,0.0));
  border: 1px solid rgba(16,185,129,0.25);
  border-radius: 18px;
  padding: 18px 20px;
}
.card {
  border: 1px solid rgba(148,163,184,0.35);
  border-radius: 16px;
  padding: 14px 16px;
  background: rgba(255,255,255,0.04);
}
.small { opacity: .8; }
.kpi {
  border: 1px solid rgba(148,163,184,0.35);
  border-radius: 14px;
  padding: 10px 12px;
  background: rgba(255,255,255,0.03);
}
hr { border: none; border-top: 1px solid rgba(148,163,184,0.25); margin: 12px 0; }
</style>
""", unsafe_allow_html=True)

# ======================== HELPERS ========================
def clamp(x, a, b):
    return max(a, min(b, x))

def fmt_money(x, dp=2):
    try:
        return f"{x:,.{dp}f}"
    except Exception:
        return str(x)

def risk_note(leverage, sl_pct):
    lev = max(1.0, float(leverage))
    sl = max(0.1, float(sl_pct))
    score = (lev * (100.0 / sl))
    norm = clamp((math.log10(score + 1) / 3.0) * 100.0, 0, 100)
    if norm < 35:
        label = "LOW"
    elif norm < 70:
        label = "MEDIUM"
    else:
        label = "HIGH"
    return norm, label

def liquidation_approx_cross(entry, leverage, side="LONG", mm=0.005):
    L = max(1.0, float(leverage))
    e = float(entry)
    if e <= 0:
        return None
    if side.upper() == "LONG":
        return e * (1 - (1 / L) + mm)
    else:
        return e * (1 + (1 / L) - mm)

def pos_size_from_risk(equity, risk_pct, entry, sl_price, side="LONG"):
    eq = float(equity)
    rp = float(risk_pct) / 100.0
    e = float(entry)
    sl = float(sl_price)
    if eq <= 0 or rp <= 0 or e <= 0:
        return None
    risk_amount = eq * rp
    if side.upper() == "LONG":
        dist = max(1e-9, e - sl)
    else:
        dist = max(1e-9, sl - e)
    qty = risk_amount / dist
    notional = qty * e
    return qty, notional, risk_amount

def grid_levels(lower, upper, n_levels):
    lo = float(lower)
    hi = float(upper)
    n = int(n_levels)
    if n < 2:
        n = 2
    if lo >= hi:
        return []
    step = (hi - lo) / (n - 1)
    return [lo + i * step for i in range(n)]

# ======================== LOGIN ========================
if not st.session_state.is_admin:
    st.markdown("""
    <div class="hero">
      <h1 style="margin:0;">💹 ElBuni Strategy PRO</h1>
      <div class="small">Private Trading Dashboard</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pin = st.text_input("🔐 Shkruaj PIN-in", type="password").strip()
        if pin:
            if pin == ADMIN_PIN:
                st.session_state.is_admin = True
                st.success("✅ Login i suksesshëm!")
                st.rerun()
            else:
                st.error("❌ PIN i gabuar")
    st.stop()

# ======================== MAIN APP ========================
st.markdown("""
<div class="hero">
  <h1 style="margin:0;">💹 ElBuni Strategy PRO</h1>
  <div class="small">Private • Manual • TP/SL • GRID • Shields • BP • Journal</div>
</div>
""", unsafe_allow_html=True)

st.write("")

tabs = st.tabs(["📌 Manual", "🎯 TP & SL", "🧱 GRID", "🛡️ Shields", "🧮 BP (Hedge)", "📝 Journal"])

# ===================== TAB 1: MANUAL =====================
with tabs[0]:
    st.subheader("📌 Manual – Setup i shpejtë")
    st.markdown("""
**Rregulla bazë (praktike):**
- Përdor **Risk %** (p.sh. 0.5% – 2%).
- Vendos **SL** para se ta hapësh pozicionin.
- Leverage rrit rrezikun → mos e përdor kot.
- Mbaj shënime në Journal që të përmirësohesh.
""")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="kpi"><b>Rekomandim Risk</b><br/>0.5% – 2% / trade</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="kpi"><b>Rregull</b><br/>SL para trade</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="kpi"><b>Disiplinë</b><br/>Mos e zhvendos SL pa plan</div>', unsafe_allow_html=True)

# ===================== TAB 2: TP & SL =====================
with tabs[1]:
    st.subheader("🎯 TP & SL – Kalkulator (Long / Short)")

    col1, col2 = st.columns([1, 1])
    with col1:
        side = st.selectbox("Drejtimi", ["LONG", "SHORT"])
        entry = st.number_input("Entry Price", min_value=0.0, value=1.0000, step=0.0001, format="%.6f")
        equity = st.number_input("Kapitali (USDT)", min_value=0.0, value=1000.0, step=10.0)
        leverage = st.number_input("Leverage (x)", min_value=1.0, value=5.0, step=1.0)
        risk_pct = st.number_input("Risk % (nga kapitali)", min_value=0.1, value=1.0, step=0.1)

    with col2:
        sl_pct = st.number_input("SL % (nga Entry)", min_value=0.1, value=2.0, step=0.1)
        tp1_pct = st.number_input("TP1 %", min_value=0.1, value=2.0, step=0.1)
        tp2_pct = st.number_input("TP2 %", min_value=0.1, value=4.0, step=0.1)
        tp3_pct = st.number_input("TP3 %", min_value=0.1, value=6.0, step=0.1)

    if side == "LONG":
        sl_price = entry * (1 - sl_pct / 100.0)
        tp1 = entry * (1 + tp1_pct / 100.0)
        tp2 = entry * (1 + tp2_pct / 100.0)
        tp3 = entry * (1 + tp3_pct / 100.0)
    else:
        sl_price = entry * (1 + sl_pct / 100.0)
        tp1 = entry * (1 - tp1_pct / 100.0)
        tp2 = entry * (1 - tp2_pct / 100.0)
        tp3 = entry * (1 - tp3_pct / 100.0)

    liq = liquidation_approx_cross(entry, leverage, side=side, mm=0.005)
    ps = pos_size_from_risk(equity, risk_pct, entry, sl_price, side=side)

    st.markdown("---")
    a, b, c = st.columns(3)
    with a:
        st.markdown(f'<div class="card"><b>SL Price</b><br/>{sl_price:.6f}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card"><b>TP1</b><br/>{tp1:.6f}</div>', unsafe_allow_html=True)
    with b:
        st.markdown(f'<div class="card"><b>TP2</b><br/>{tp2:.6f}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card"><b>TP3</b><br/>{tp3:.6f}</div>', unsafe_allow_html=True)
    with c:
        st.markdown(f'<div class="card"><b>Liq (Approx)</b><br/>{liq:.6f if liq else "—"}</div>', unsafe_allow_html=True)

    if ps:
        qty, notional, risk_amount = ps
        sens, label = risk_note(leverage, sl_pct)
        st.markdown("#### 📌 Position Size (me Risk %)")
        st.write(f"- Risk Amount: **{fmt_money(risk_amount)} USDT**")
        st.write(f"- Qty (afërsisht): **{fmt_money(qty, 6)}**")
        st.write(f"- Notional: **{fmt_money(notional)} USDT**")
        st.write(f"- Ndjeshmëria e rrezikut: **{label}** ({sens:.0f}/100)")
    else:
        st.info("Plotëso vlera valide për Position Size.")

    st.caption("Shënim: Likuidimi është afërsim (varet nga exchange/fees/MM).")

# ===================== TAB 3: GRID =====================
with tabs[2]:
    st.subheader("🧱 GRID – Gjenerues niveleve")

    g1, g2 = st.columns(2)
    with g1:
        g_lower = st.number_input("Lower Bound", min_value=0.0, value=0.9000, step=0.0001, format="%.6f")
        g_upper = st.number_input("Upper Bound", min_value=0.0, value=1.1000, step=0.0001, format="%.6f")
    with g2:
        g_levels = st.number_input("Nr. Niveleve", min_value=2, value=11, step=1)
        per_level_usdt = st.number_input("USDT për nivel (opsional)", min_value=0.0, value=0.0, step=10.0)

    levels = grid_levels(g_lower, g_upper, g_levels)
    if not levels:
        st.error("Lower duhet të jetë më i vogël se Upper.")
    else:
        step = (g_upper - g_lower) / (max(2, int(g_levels)) - 1)
        st.markdown(f"""
<div class="card">
<b>Hap (Step):</b> {step:.6f}<br/>
<b>Nivele:</b> {len(levels)}
</div>
""", unsafe_allow_html=True)

        rows = [{"#": i+1, "Level": lv} for i, lv in enumerate(levels)]
        st.dataframe(rows, use_container_width=True)

        if per_level_usdt > 0:
            total = per_level_usdt * len(levels)
            st.success(f"Total alokim: {fmt_money(total)} USDT")

# ===================== TAB 4: SHIELDS =====================
with tabs[3]:
    st.subheader("🛡️ Shields – Kontroll rreziku")

    s1, s2 = st.columns(2)
    with s1:
        lev = st.number_input("Leverage (x)", min_value=1.0, value=5.0, step=1.0, key="s_lev")
        slp = st.number_input("SL %", min_value=0.1, value=2.0, step=0.1, key="s_slp")
        daily_max_loss = st.number_input("Daily Max Loss %", min_value=0.5, value=3.0, step=0.5)
    with s2:
        trades_per_day = st.number_input("Max Trades/Day", min_value=1, value=5, step=1)
        cool_down = st.number_input("Cooldown (min) pas humbje", min_value=0, value=30, step=5)
        news_mode = st.checkbox("News Mode (ul rrezikun)", value=False)

    sens, label = risk_note(lev, slp)
    adj = 0.7 if news_mode else 1.0
    suggested_risk = clamp((1.5 - (sens/100)*1.2) * adj, 0.25, 1.5)

    st.markdown("---")
    st.markdown(f"""
<div class="card">
<b>Ndjeshmëria:</b> {label} ({sens:.0f}/100)<br/>
<b>Risk i sugjeruar / trade:</b> {suggested_risk:.2f}%<br/>
<b>Daily Stop:</b> {daily_max_loss:.1f}% • <b>Max Trades:</b> {int(trades_per_day)} • <b>Cooldown:</b> {int(cool_down)} min
</div>
""", unsafe_allow_html=True)

    st.markdown("#### Rregulla të shpejta")
    st.markdown("""
- 2 humbje rresht → ndalo, cooldown.
- News Mode → ul lev / risk.
- Mos e hap trade-in pa SL.
""")

# ===================== TAB 5: BP (HEDGE) =====================
with tabs[4]:
    st.subheader("🧮 BP (Hedge) – Split Spot/Futures (model i thjeshtë)")

    b1, b2 = st.columns(2)
    with b1:
        total_usdt = st.number_input("Total kapital (USDT)", min_value=0.0, value=1000.0, step=50.0)
        split_spot = st.slider("Spot %", min_value=0, max_value=100, value=70)
        split_fut = 100 - split_spot
        st.write(f"Futures %: **{split_fut}%**")
    with b2:
        fut_lev = st.number_input("Futures Leverage", min_value=1.0, value=3.0, step=1.0)
        hedge_ratio = st.slider("Hedge Ratio (sa % mbron Spot)", 0, 200, 100)

    spot_usdt = total_usdt * split_spot / 100.0
    fut_margin = total_usdt * split_fut / 100.0
    fut_notional = fut_margin * fut_lev
    hedge_target = spot_usdt * (hedge_ratio / 100.0)

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="card"><b>Spot</b><br/>{fmt_money(spot_usdt)} USDT</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="card"><b>Futures Margin</b><br/>{fmt_money(fut_margin)} USDT</div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="card"><b>Futures Notional</b><br/>{fmt_money(fut_notional)} USDT</div>', unsafe_allow_html=True)

    st.markdown("#### Hedge Suggestion")
    st.write(f"- Target Hedge Notional: **{fmt_money(hedge_target)} USDT**")
    if fut_notional < hedge_target:
        st.warning("Mbrojtja është më e vogël se target (sipas këtij modeli).")
    else:
        st.success("Mbrojtja e arrin/kalon target (sipas këtij modeli).")

    st.caption("Shënim: Model i thjeshtë. Jo këshillë financiare.")

# ===================== TAB 6: JOURNAL =====================
with tabs[5]:
    st.subheader("📝 Journal – Shënime trade")

    j1, j2, j3 = st.columns(3)
    with j1:
        j_pair = st.text_input("Pair", value="BTC/USDT")
        j_side = st.selectbox("Side", ["LONG", "SHORT"])
    with j2:
        j_entry = st.number_input("Entry", min_value=0.0, value=0.0, step=0.1)
        j_sl = st.number_input("SL", min_value=0.0, value=0.0, step=0.1)
    with j3:
        j_tp = st.number_input("TP", min_value=0.0, value=0.0, step=0.1)
        j_note = st.text_input("Note", value="")

    if st.button("➕ Shto në Journal"):
        st.session_state.journal.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "pair": j_pair,
            "side": j_side,
            "entry": j_entry,
            "sl": j_sl,
            "tp": j_tp,
            "note": j_note
        })
        st.success("U shtua!")

    st.markdown("---")
    if st.session_state.journal:
        st.dataframe(st.session_state.journal, use_container_width=True)

        import pandas as pd
        df = pd.DataFrame(st.session_state.journal)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Shkarko CSV", data=csv, file_name="elbuni_journal.csv", mime="text/csv")

        if st.button("🗑️ Fshij Journal"):
            st.session_state.journal = []
            st.warning("Journal u fshi.")
    else:
        st.info("Journal është bosh.")

# ======================== LOGOUT ========================
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout"):
    st.session_state.is_admin = False
    st.rerun()
