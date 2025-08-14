import streamlit as st
from models.gemini_client import start_dream_analysis_chat, GEMINI_API_KEY
import pyperclip
import time
from database.db_manager import add_dream_analysis, list_dream_analyses, delete_dream_analysis
import pandas as pd
from models.image_gen import generate_dream_image

# --- Authentication Check ---
if not st.session_state.get('logged_in') and not st.session_state.get('is_guest'):
    st.error("Bu sayfayı görüntülemek için lütfen giriş yapın veya misafir olarak devam edin.")
    st.stop()

st.set_page_config(page_title="🔮 Rüya Analizi", page_icon="🔮")

st.title("🔮 Rüya Analizi")
st.markdown("Rüyanızı aşağıya yazın, AI analizini başlatın!")

# --- Guest User Warning ---
if st.session_state.get('is_guest'):
    st.warning("Şu anda misafir modundasınız. Yaptığınız analizler ve görseller kaydedilmeyecektir.")

# --- Session State Initialization for Chat ---
if "dream_chat_session" not in st.session_state:
    st.session_state.dream_chat_session = None
if "dream_messages" not in st.session_state:
    st.session_state.dream_messages = []
if "dream_analysis_started" not in st.session_state:
    st.session_state.dream_analysis_started = False

# --- Session State Initialization for Image Visualization (existing) ---
if "dream_image_path" not in st.session_state:
    st.session_state.dream_image_path = None
if "visualize_mode" not in st.session_state:
    st.session_state.visualize_mode = False

RATE_LIMIT_SECONDS = 60 # Not directly used for chat, but kept for reference

# --- Initial Dream Input Form ---
if not st.session_state.dream_analysis_started:
    with st.form("initial_dream_form"):
        dream_text_input = st.text_area("Rüyanızı detaylıca anlatın:", height=200, key="initial_dream_text")
        submitted_initial = st.form_submit_button("Analiz Et ve Sohbeti Başlat")

    if submitted_initial and dream_text_input:
        if not GEMINI_API_KEY:
            st.error("Gemini API anahtarı bulunamadı. Lütfen .env dosyanızı kontrol edin.")
        else:
            with st.spinner("Rüya analizi başlatılıyor..."):
                st.session_state.dream_chat_session = start_dream_analysis_chat()
                if st.session_state.dream_chat_session:
                    # Send initial dream and get first response
                    ai_response = st.session_state.dream_chat_session.send_message(dream_text_input)
                    st.session_state.dream_messages.append({"role": "user", "content": dream_text_input})
                    st.session_state.dream_messages.append({"role": "model", "content": ai_response})
                    st.session_state.dream_analysis_started = True
                    # Save initial analysis for logged-in users
                    if st.session_state.get('logged_in'):
                        add_dream_analysis(st.session_state['user_id'], dream_text_input, ai_response) # Save initial response
                    st.rerun()
                else:
                    st.error("Sohbet oturumu başlatılamadı. API anahtarını kontrol edin.")

# --- Chat Interface ---
if st.session_state.dream_analysis_started:
    st.markdown("---")
    st.subheader("💬 Rüya Analizi Sohbeti")

    # Display chat messages from history
    for message in st.session_state.dream_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input for new messages
    if prompt := st.chat_input("Rüyanız hakkında daha fazla soru sorun veya yorum yapın..."):
        st.session_state.dream_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("model"):
            with st.spinner("AI yanıtlıyor..."):
                ai_response = st.session_state.dream_chat_session.send_message(prompt)
                st.markdown(ai_response)
                st.session_state.dream_messages.append({"role": "model", "content": ai_response})

    col_chat_actions = st.columns(2)
    with col_chat_actions[0]:
        if st.button("🔄 Yeni Sohbet Başlat"):
            st.session_state.dream_chat_session = None
            st.session_state.dream_messages = []
            st.session_state.dream_analysis_started = False
            st.session_state.dream_image_path = None # Clear image for new chat
            st.session_state.visualize_mode = False
            st.rerun()
    with col_chat_actions[1]:
        # --- Dream Visualization (Available for Guests too, but won't be saved) ---
        if st.session_state.dream_image_path:
            st.image(st.session_state.dream_image_path, caption="AI ile oluşturulan rüya görseli", use_column_width=True)
            if st.button("Yeni Görsel Oluştur"):
                st.session_state.visualize_mode = True
                st.session_state.dream_image_path = None # Clear old image
                st.rerun()
        elif st.session_state.visualize_mode:
            with st.form("visualize_form"):
                st.info("Görsel oluşturmak için aşağıdaki metni düzenleyin veya kendi isteminizi yazın.")
                # Suggest a prompt from the first 150 chars of the dream
                # Use the initial dream text for suggestion, not the chat history
                suggested_prompt = st.session_state.dream_messages[0]["content"][:150] + "..." if st.session_state.dream_messages else ""
                image_prompt = st.text_area("Görselleştirme İstemi (Prompt)", value=suggested_prompt, height=100)
                
                submitted_visualize = st.form_submit_button("Görseli Oluştur")
                if submitted_visualize:
                    with st.spinner("Rüya görseli üretiliyor..."):
                        image_path = generate_dream_image(image_prompt)
                        if image_path:
                            st.session_state.dream_image_path = image_path
                        else:
                            st.error("Görsel üretilemedi.")
                    st.session_state.visualize_mode = False
                    st.rerun()
        else:
            if st.button("🎨 Rüyamı Görselleştir"):
                st.session_state.visualize_mode = True
                st.rerun()

# --- History Section (Logged-in users only) ---
if st.session_state.get('logged_in'):
    st.markdown("---")
    st.subheader("🕑 Rüya Analizi Geçmişi")
    
    records = list_dream_analyses(st.session_state['user_id'], limit=30)
    if not records:
        st.info("Henüz analiz geçmişiniz yok.")
    else:
        df = pd.DataFrame([{"id": r.id, "created_at": r.created_at, "dream_text": r.dream_text} for r in records])
        for _, rec in df.iterrows():
            with st.expander(f"{rec['created_at'].strftime('%d.%m.%Y %H:%M')} - Rüya #{rec['id']}"):
                st.markdown(f"**Rüya:**\n{rec['dream_text']}")
                if st.button(f"❌ Sil", key=f"del_dream_{rec['id']}"):
                    delete_dream_analysis(rec['id'])
                    st.success("Kayıt silindi!")
                    st.rerun()