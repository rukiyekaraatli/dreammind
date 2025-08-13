import streamlit as st
from models.gemini_client import analyze_dream
import pyperclip
import time
from database.db_manager import add_dream_analysis, list_dream_analyses, delete_dream_analysis
import pandas as pd
from models.image_gen import generate_dream_image

st.set_page_config(page_title="🔮 Rüya Analizi", page_icon="🔮")

st.title("🔮 Rüya Analizi")
st.markdown("""
Rüyanızı aşağıya yazın, AI analizini başlatın!
""")

# Session state ile cache (Streamlit best practice)
if "dream_analysis_result" not in st.session_state:
    st.session_state["dream_analysis_result"] = None
if "dream_text" not in st.session_state:
    st.session_state["dream_text"] = ""
if "last_analysis_time" not in st.session_state:
    st.session_state["last_analysis_time"] = 0.0
if "dream_image_path" not in st.session_state:
    st.session_state["dream_image_path"] = None
if "dream_image_loading" not in st.session_state:
    st.session_state["dream_image_loading"] = False
if "dream_image_error" not in st.session_state:
    st.session_state["dream_image_error"] = None

RATE_LIMIT_SECONDS = 60  # 1 dakikada 1 analiz

with st.form("dream_form"):
    dream_text = st.text_area("Rüyanızı detaylıca anlatın:", value=st.session_state["dream_text"], height=200)
    submitted = st.form_submit_button("Analiz Et")

if submitted:
    now = time.time()
    elapsed = now - st.session_state["last_analysis_time"]
    if elapsed < RATE_LIMIT_SECONDS:
        st.warning(f"Çok sık analiz denemesi! Lütfen {int(RATE_LIMIT_SECONDS - elapsed)} saniye bekleyin.")
    else:
        st.session_state["dream_text"] = dream_text
        with st.spinner("AI analiz ediyor..."):
            try:
                result = analyze_dream(dream_text)
                st.session_state["dream_analysis_result"] = result
                st.session_state["last_analysis_time"] = now
                add_dream_analysis(dream_text, result)
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")
                st.session_state["dream_analysis_result"] = None

# Sonuç gösterimi ve UI iyileştirmeleri
if st.session_state["dream_analysis_result"]:
    st.markdown("---")
    st.subheader("🔍 Analiz Sonucu")
    st.markdown(f"""
    <div style='background-color:#F0F2F6; padding:20px; border-radius:12px; border:1px solid #FF6B6B;'>
    <pre style='white-space:pre-wrap; font-size:1.1em;'>{st.session_state['dream_analysis_result']}</pre>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,2])
    with col1:
        if st.button("📋 Kopyala"):
            try:
                pyperclip.copy(st.session_state["dream_analysis_result"])
                st.success("Analiz sonucu panoya kopyalandı!")
            except Exception:
                st.warning("Kopyalama için pyperclip modülü yüklü olmalı.")
    with col2:
        if st.button("🧹 Temizle"):
            st.session_state["dream_analysis_result"] = None
            st.session_state["dream_text"] = ""
            st.session_state["dream_image_path"] = None
            st.session_state["dream_image_error"] = None
            st.rerun()
    with col3:
        st.caption("AI analizi sadece bilgilendirme amaçlıdır.")

    # --- Rüyayı Görselleştir ---
    st.markdown("<br>", unsafe_allow_html=True)
    if st.session_state["dream_image_path"]:
        st.image(st.session_state["dream_image_path"], caption="AI ile oluşturulan rüya görseli", use_column_width=True)
        with open(st.session_state["dream_image_path"], "rb") as img_file:
            st.download_button("Görseli İndir", img_file, file_name="ruya_gorseli.png", mime="image/png")
    elif st.session_state["dream_image_loading"]:
        st.info("Görsel üretiliyor, lütfen bekleyin...")
    else:
        if st.button("🎨 Rüyamı Görselleştir"):
            st.session_state["dream_image_loading"] = True
            st.session_state["dream_image_error"] = None
            st.rerun()

    if st.session_state["dream_image_loading"]:
        with st.spinner("Rüya görseli üretiliyor..."):
            prompt = st.session_state["dream_text"][:200]  # Kısa prompt
            image_path = generate_dream_image(prompt)
            if image_path:
                st.session_state["dream_image_path"] = image_path
            else:
                st.session_state["dream_image_error"] = "Görsel üretilemedi. Lütfen daha sonra tekrar deneyin."
            st.session_state["dream_image_loading"] = False
            
    if st.session_state["dream_image_error"]:
        st.error(st.session_state["dream_image_error"])

# --- Rüya Analizi Geçmişi: Arama ve Filtreleme ---
st.markdown("---")
st.subheader("🕑 Rüya Analizi Geçmişi (Son 30)")

with st.expander("🔎 Geçmişte Ara/Filtrele", expanded=False):
    col1, col2 = st.columns([2,3])
    with col1:
        date_start = st.date_input("Başlangıç Tarihi", value=None, key="dream_date_start")
    with col2:
        date_end = st.date_input("Bitiş Tarihi", value=None, key="dream_date_end")
    keyword = st.text_input("Rüya veya analizde ara (anahtar kelime)", key="dream_keyword")

records = list_dream_analyses(limit=90)
if records:
    df = pd.DataFrame([
        {"id": rec.id, "created_at": rec.created_at, "dream_text": rec.dream_text, "analysis_result": rec.analysis_result} for rec in records
    ])
    # Filtre uygula
    if date_start:
        df = df[df["created_at"].dt.date >= date_start]
    if date_end:
        df = df[df["created_at"].dt.date <= date_end]
    if keyword:
        df = df[df["dream_text"].fillna("").str.contains(keyword, case=False, na=False) |
                df["analysis_result"].fillna("").str.contains(keyword, case=False, na=False)]
    # Son 30 kaydı göster
    df = df.sort_values("created_at", ascending=False).head(30)
    if df.empty:
        st.info("Filtreye uyan kayıt bulunamadı.")
    else:
        for _, rec in df.iterrows():
            with st.expander(f"{rec['created_at'].strftime('%d.%m.%Y %H:%M')} - Rüya #{rec['id']}", expanded=False):
                st.markdown(f"**Rüya:**\n{rec['dream_text']}")
                st.markdown(f"**Analiz:**\n{rec['analysis_result']}")
                col_del, _ = st.columns([1,5])
                with col_del:
                    if st.button(f"❌ Sil", key=f"del_dream_{rec['id']}"):
                        delete_dream_analysis(rec['id'])
                        st.success("Kayıt silindi!")
                        st.rerun()
else:
    st.info("Henüz analiz geçmişiniz yok.") 