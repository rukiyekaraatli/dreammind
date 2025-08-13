import streamlit as st
from datetime import date, datetime
from database.db_manager import add_mood_record, list_mood_records, delete_mood_record
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="😊 Mood Tracker", page_icon="😊")

st.markdown("""
<style>
    .mood-header {color: #9C27B0; font-size: 2.2rem; font-weight: bold; margin-bottom: 0.5rem;}
    .mood-card {background: #F5F5F5; border-left: 6px solid #9C27B0; border-radius: 12px; padding: 1rem; margin-bottom: 0.5rem;}
    .mood-expander .streamlit-expanderHeader {color: #9C27B0; font-weight: bold;}
    .mood-btn {background: #E1BEE7; color: #262730; border-radius: 8px; border: none; padding: 0.4rem 1.2rem; font-weight: 600;}
    .mood-btn:hover {background: #9C27B0; color: #fff;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="mood-header">😊 Mood Tracker</div>', unsafe_allow_html=True)
st.markdown("Günlük ruh halinizi kaydedin ve değişimi takip edin.")

if "mood_result" not in st.session_state:
    st.session_state["mood_result"] = None

with st.form("mood_form"):
    mood = st.selectbox("Bugünkü ruh haliniz?", ["😊 Mutlu", "😢 Üzgün", "😠 Sinirli", "😨 Korkmuş", "😲 Şaşkın", "🤢 İğrenmiş", "😐 Nötr"])
    note = st.text_input("Eklemek istediğiniz bir not var mı?")
    submitted = st.form_submit_button("Kaydet", use_container_width=True)

if submitted:
    add_mood_record(mood, note)
    st.session_state["mood_result"] = f"{date.today()} - Ruh hali kaydedildi: {mood}"
    st.rerun()

if st.session_state["mood_result"]:
    st.success(st.session_state["mood_result"])

# --- Mood Trend Grafiği ---
st.markdown("---")
st.markdown('<span style="color:#9C27B0;font-size:1.3rem;font-weight:bold;">📈 Mood Trend Grafiği</span>', unsafe_allow_html=True)
records = list_mood_records(limit=90)  # Son 3 ayı al
if records:
    df = pd.DataFrame([
        {"date": rec.created_at.date(), "mood": rec.mood, "note": rec.note} for rec in records
    ])
    df = df.sort_values("date").drop_duplicates("date", keep="last")
    mood_order = ["😊 Mutlu", "😐 Nötr", "😲 Şaşkın", "😨 Korkmuş", "😢 Üzgün", "😠 Sinirli", "🤢 İğrenmiş"]
    df["mood"] = pd.Categorical(df["mood"], categories=mood_order, ordered=True)
    mood_colors = {
        "😊 Mutlu": "#9C27B0",
        "😐 Nötr": "#B39DDB",
        "😲 Şaşkın": "#90CAF9",
        "😨 Korkmuş": "#9575CD",
        "😢 Üzgün": "#F8BBD0",
        "😠 Sinirli": "#F44336",
        "🤢 İğrenmiş": "#795548"
    }
    fig = px.line(df, x="date", y="mood", markers=True, color="mood",
                  color_discrete_map=mood_colors,
                  category_orders={"mood": mood_order},
                  labels={"date": "Tarih", "mood": "Ruh Hali"},
                  title="Son 3 Ay Mood Değişimi")
    fig.update_layout(
        plot_bgcolor="#F5F5F5",
        paper_bgcolor="#FFFFFF",
        font=dict(color="#262730"),
        title_font=dict(size=20, color="#9C27B0"),
        legend_title_text="Ruh Hali",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Grafik için yeterli mood kaydı yok.")

# --- Mood Geçmişi: Arama ve Filtreleme ---
st.markdown("---")
st.markdown('<span style="color:#9C27B0;font-size:1.3rem;font-weight:bold;">🕑 Mood Geçmişi (Son 30)</span>', unsafe_allow_html=True)

# Filtreler
with st.expander("🔎 Geçmişte Ara/Filtrele", expanded=False):
    col1, col2, col3 = st.columns([2,2,3])
    with col1:
        date_start = st.date_input("Başlangıç Tarihi", value=None, key="mood_date_start")
    with col2:
        date_end = st.date_input("Bitiş Tarihi", value=None, key="mood_date_end")
    with col3:
        mood_filter = st.selectbox("Mood Filtrele", ["Tümü", "😊 Mutlu", "😢 Üzgün", "😠 Sinirli", "😨 Korkmuş", "😲 Şaşkın", "🤢 İğrenmiş", "😐 Nötr"], key="mood_filter")
    keyword = st.text_input("Notlarda Ara (anahtar kelime)", key="mood_keyword")

records = list_mood_records(limit=90)
if records:
    df = pd.DataFrame([
        {"id": rec.id, "created_at": rec.created_at, "mood": rec.mood, "note": rec.note} for rec in records
    ])
    # Filtre uygula
    if date_start:
        df = df[df["created_at"].dt.date >= date_start]
    if date_end:
        df = df[df["created_at"].dt.date <= date_end]
    if mood_filter and mood_filter != "Tümü":
        df = df[df["mood"] == mood_filter]
    if keyword:
        df = df[df["note"].fillna("").str.contains(keyword, case=False, na=False)]
    # Son 30 kaydı göster
    df = df.sort_values("created_at", ascending=False).head(30)
    if df.empty:
        st.info("Filtreye uyan kayıt bulunamadı.")
    else:
        for _, rec in df.iterrows():
            with st.expander(f"{rec['created_at'].strftime('%d.%m.%Y %H:%M')} - {rec['mood']}", expanded=False):
                st.markdown(f'<div class="mood-card">', unsafe_allow_html=True)
                st.markdown(f"**Not:** {rec['note'] if rec['note'] else '-'}")
                col_del, _ = st.columns([1,5])
                with col_del:
                    if st.button(f"❌ Sil", key=f"del_mood_{rec['id']}"):
                        delete_mood_record(rec['id'])
                        st.success("Kayıt silindi!")
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("Henüz mood geçmişiniz yok.") 