import streamlit as st
import pandas as pd
import plotly.express as px
from database.db_manager import list_dream_analyses, list_mood_records, list_character_therapies

# --- Authentication Check ---
if not st.session_state.get('logged_in') and not st.session_state.get('is_guest'):
    st.error("Bu sayfayı görüntülemek için lütfen giriş yapın veya misafir olarak devam edin.")
    st.stop()

st.set_page_config(page_title="📊 Analytics", page_icon="📊")
st.title("📊 Kişisel Analizleriniz")

# --- Guest User Message ---
if st.session_state.get('is_guest'):
    st.warning("Bu alanı görmek için lütfen giriş yapın.")
    st.info("Giriş yaptığınızda, kaydettiğiniz rüya, ruh hali ve terapi verilerinizin görsel analizlerini burada bulabilirsiniz.")
    st.stop()

# --- Analytics for Logged-in Users ---
if st.session_state.get('logged_in'):
    user_id = st.session_state['user_id']

    # Load data
    dream_records = list_dream_analyses(user_id, limit=1000)
    mood_records = list_mood_records(user_id, limit=1000)
    therapy_records = list_character_therapies(user_id, limit=1000)

    st.markdown("### Genel Bakış")
    col1, col2, col3 = st.columns(3)
    col1.metric("Toplam Rüya Analizi", len(dream_records))
    col2.metric("Toplam Mood Kaydı", len(mood_records))
    col3.metric("Toplam Terapi Seansı", len(therapy_records))

    st.markdown("---")

    # Mood Distribution Chart
    if mood_records:
        st.subheader("Ruh Hali Dağılımı")
        mood_df = pd.DataFrame([r.mood for r in mood_records], columns=['mood'])
        mood_counts = mood_df['mood'].value_counts().reset_index()
        mood_counts.columns = ['mood', 'count']
        fig = px.pie(mood_counts, names='mood', values='count', title="Kaydedilen Ruh Hallerinin Dağılımı", hole=.3)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Ruh hali grafiği için henüz yeterli veri yok.")

    # Further analytics can be added here