import streamlit as st
from datetime import date
from database.db_manager import add_mood_record, list_mood_records, delete_mood_record
import pandas as pd
import plotly.express as px

# --- Authentication Check ---

if not st.session_state.get('logged_in') and not st.session_state.get('is_guest'):
    st.error("Bu sayfayı görüntülemek için lütfen giriş yapın veya misafir olarak devam edin.")
    st.stop()

st.set_page_config(page_title="😊 Mood Tracker", page_icon="😊")

st.title("😊 Mood Tracker")
st.markdown("Günlük ruh halinizi kaydedin ve değişimi takip edin.")

# --- Guest User Warning ---
if st.session_state.get('is_guest'):
    st.warning("Şu anda misafir modundasınız. Ruh hali kayıtlarınız tutulmayacaktır.")

# --- Mood Submission Form (Disabled for guests) ---
with st.form("mood_form"):
    mood = st.selectbox("Bugünkü ruh haliniz?", ["😊 Mutlu", "😢 Üzgün", "😠 Sinirli", "😨 Korkmuş", "🫥 Depresyonda","😲 Şaşkın", "🤢 İğrenmiş", "😐 Nötr","🥲 Duygusal","💖 Heyecanlı","😥 Kaygılı","🥵Başından aşağı kaynar sular dökülmüş","🤒 Hasta"])
    note = st.text_input("Eklemek istediğiniz bir not var mı?")
    submitted = st.form_submit_button("Kaydet", use_container_width=True, disabled=st.session_state.get('is_guest'))

if submitted and st.session_state.get('logged_in'):
    add_mood_record(st.session_state['user_id'], mood, note)
    st.success(f"{date.today()} - Ruh hali kaydedildi: {mood}")
    st.rerun()

# --- Analytics and History (Logged-in users only) ---
if st.session_state.get('logged_in'):
    st.markdown("---")
    st.subheader("📈 Mood Trend Grafiği")
    records = list_mood_records(st.session_state['user_id'], limit=90)
    
    if not records or len(records) < 2:
        st.info("Grafik çizmek için en az 2 ruh hali kaydınız olmalıdır.")
    else:
        df = pd.DataFrame([{"date": r.created_at.date(), "mood": r.mood} for r in records])
        df = df.sort_values("date").drop_duplicates("date", keep="last")
        mood_order = ["😊 Mutlu", "😢 Üzgün", "😠 Sinirli", "😨 Korkmuş", "🫥 Depresyonda","😲 Şaşkın", "🤢 İğrenmiş", "😐 Nötr","🥲 Duygusal","💖 Heyecanlı","😥 Kaygılı","🥵Başından aşağı kaynar sular dökülmüş","🤒 Hasta"]
        df["mood"] = pd.Categorical(df["mood"], categories=mood_order, ordered=True)
        fig = px.line(df, x="date", y="mood", markers=True, title="Ruh Hali Değişim Grafiği")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("🕑 Mood Geçmişi")
    if not records:
        st.info("Henüz mood geçmişiniz yok.")
    else:
        for rec in records:
            with st.expander(f"{rec.created_at.strftime('%d.%m.%Y %H:%M')} - {rec.mood}"):
                st.write(f"**Not:** {rec.note if rec.note else '-'}")
                if st.button(f"❌ Sil", key=f"del_mood_{rec.id}"):
                    delete_mood_record(rec.id)
                    st.success("Kayıt silindi!")
                    st.rerun()