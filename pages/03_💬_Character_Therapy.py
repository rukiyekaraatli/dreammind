import streamlit as st
from database.db_manager import add_character_therapy, list_character_therapies, delete_character_therapy
from models.gemini_client import character_therapy_response

st.set_page_config(page_title="💬 Karakter Terapisi", page_icon="💬")

st.markdown("""
<style>
    .therapy-header {color: #9C27B0; font-size: 2.2rem; font-weight: bold; margin-bottom: 0.5rem;}
    .therapy-card {background: #F5F5F5; border-left: 6px solid #9C27B0; border-radius: 12px; padding: 1rem; margin-bottom: 0.5rem;}
    .therapy-expander .streamlit-expanderHeader {color: #9C27B0; font-weight: bold;}
    .therapy-btn {background: #E1BEE7; color: #262730; border-radius: 8px; border: none; padding: 0.4rem 1.2rem; font-weight: 600;}
    .therapy-btn:hover {background: #9C27B0; color: #fff;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="therapy-header">💬 Karakter Terapisi</div>', unsafe_allow_html=True)
st.markdown("Favori karakterinizi seçin ve AI ile terapi başlatın.")

characters = ["Sherlock Holmes", "Firdevs Hanım","Ramiz Dayı","Aksakallı Dede", "İsmail Abi","Burhan Altıntop","Carrie Bradshaw", "Yılmaz"]
selected_character = st.selectbox("Karakter Seçimi", characters)

st.info(f"Seçili karakter: {selected_character}")

if "therapy_result" not in st.session_state:
    st.session_state["therapy_result"] = None

with st.form("therapy_form"):
    user_input = st.text_area("Sorununuzu veya konuşmak istediğiniz konuyu yazın:")
    submitted = st.form_submit_button("Terapiye Başla", use_container_width=True)

if submitted:
    with st.spinner("Karakter yanıtlıyor..."):
        try:
            ai_response = character_therapy_response(selected_character, user_input)
            add_character_therapy(selected_character, user_input, ai_response)
            st.session_state["therapy_result"] = ai_response
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
            st.session_state["therapy_result"] = None
    st.rerun()

if st.session_state["therapy_result"]:
    st.success(st.session_state["therapy_result"])

st.markdown("---")
st.markdown('<span style="color:#9C27B0;font-size:1.3rem;font-weight:bold;">🕑 Terapi Geçmişi (Son 30)</span>', unsafe_allow_html=True)
records = list_character_therapies(limit=30)
if not records:
    st.info("Henüz terapi geçmişiniz yok.")
else:
    for rec in records:
        with st.expander(f"{rec.created_at.strftime('%d.%m.%Y %H:%M')} - {rec.character}", expanded=False):
            st.markdown(f'<div class="therapy-card">', unsafe_allow_html=True)
            st.markdown(f"**Soru:** {rec.user_input}")
            st.markdown(f"**Yanıt:** {rec.ai_response}")
            col_del, _ = st.columns([1,5])
            with col_del:
                if st.button(f"❌ Sil", key=f"del_therapy_{rec.id}"):
                    delete_character_therapy(rec.id)
                    st.success("Kayıt silindi!")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True) 