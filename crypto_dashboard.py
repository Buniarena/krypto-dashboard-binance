import streamlit as st

# ======================== CONFIG ========================
st.set_page_config(
    page_title="Xhamia e Bardhë – Hotël",
    page_icon="🕌",
    layout="wide"
)

ADMIN_PIN = "3579"  # 🔁 Ndryshoje kur të duash

# ======================== NDËRRO KËTO 2 VETËM (TEKSTET) ========================
TELEFONI = "__________"      # p.sh. "+389 7X XXX XXX"
XHUMAJA_ORA = "__:__"        # p.sh. "12:30"

# ======================== SESSION ========================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

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
</style>
""", unsafe_allow_html=True)

# ======================== SIDEBAR ========================
with st.sidebar:
    st.markdown("### 🕌 Xhamia e Bardhë – Hotël")

    st.markdown("#### 🔐 Admin (vetëm ti)")
    pin = st.text_input("Shkruaj PIN-in", type="password")

    if pin:
        if pin == ADMIN_PIN:
            st.session_state.is_admin = True
            st.success("✅ Admin aktiv")
        else:
            st.session_state.is_admin = False
            st.error("❌ PIN i gabuar")

    st.markdown("---")

    if st.session_state.is_admin:
        page = st.radio("Menu", ["🕌 Faqja e Xhamisë", "💹 ElBuni Strategy (Private)"], index=0)
    else:
        page = "🕌 Faqja e Xhamisë"

# ======================== PAGE: XHAMIA (PUBLIC) ========================
if page == "🕌 Faqja e Xhamisë":
    st.markdown("""
    <div class="hero">
      <h1 style="margin:0;">🕌 Xhamia e Bardhë – Hotël</h1>
      <div class="small">Faqe zyrtare • Njoftime • Oraret • Kontakt</div>
      <div class="small" style="margin-top:6px;"><b>Kryetar:</b> Bunjamin Fetai • <b>Këshilli i Xhamisë:</b> Xhamia e Bardhë</div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    colA, colB = st.columns([1.1, 0.9])

    with colA:
        st.markdown("### Mirë se vini")
        st.write(
            "Kjo faqe shërben për njoftime zyrtare, oraret e namazit, aktivitetet fetare "
            "dhe informacione për xhematin."
        )

        st.markdown("### 📢 Njoftime")
        st.markdown("""
- Aktivitetet javore
- Njoftime të Ramazanit
- Mbledhje dhe vendime të këshillit
""")

    with colB:
        st.markdown("### ⏰ Oraret e Namazit")
        st.markdown(f"""
<div class="card">
<b>Sabah:</b> __:__<br/>
<b>Dreka:</b> __:__<br/>
<b>Ikindia:</b> __:__<br/>
<b>Akshami:</b> __:__<br/>
<b>Jacia:</b> __:__<br/>
<hr style="border:none;border-top:1px solid rgba(148,163,184,0.35);margin:10px 0;">
<b>Xhumaja:</b> {XHUMAJA_ORA} (në kohën fiks)
</div>
""", unsafe_allow_html=True)

    st.markdown("---")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 📚 Mësim Kurani")
        st.write("Mësimi dhe leximi i Kuranit organizohet për:")
        st.markdown("- Fëmijë\n- Të rinj\n- Të moshuar")
        st.write("Për informata: " + TELEFONI)

    with c2:
        st.markdown("### 📍 Kontakt")
        st.markdown(f"""
<div class="card">
<b>Telefoni:</b> {TELEFONI}<br/>
<b>Lokacioni:</b> Hotël<br/>
<b>Orari:</b> E hapur çdo ditë për besimtarët
</div>
""", unsafe_allow_html=True)

# ======================== PAGE: ELBUNI (PRIVATE) ========================
elif page == "💹 ElBuni Strategy (Private)":
    if not st.session_state.is_admin:
        st.error("⛔ Kjo pjesë është vetëm për admin.")
        st.stop()

    st.title("💹 ElBuni Strategy (Private)")
    st.caption("Kjo pjesë shfaqet vetëm kur futet PIN-i.")
    st.info("👉 Këtu e ngjit kodin tënd të plotë të ElBuni (tabs/kalkulator/grid/shields/BP).")