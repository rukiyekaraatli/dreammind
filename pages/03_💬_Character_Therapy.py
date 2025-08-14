import streamlit as st
from database.db_manager import add_character_therapy, list_character_therapies, delete_character_therapy
from models.gemini_client import start_character_therapy_chat, GEMINI_API_KEY

# --- Authentication Check ---
if not st.session_state.get('logged_in') and not st.session_state.get('is_guest'):
    st.error("Bu sayfayı görüntülemek için lütfen giriş yapın veya misafir olarak devam edin.")
    st.stop()

st.set_page_config(page_title="💬 Karakter Terapisi", page_icon="💬")

st.title("💬 Karakter Terapisi")
st.markdown("Favori karakterinizi seçin ve AI ile terapi başlatın.")

# --- Guest User Warning ---
if st.session_state.get('is_guest'):
    st.warning("Şu anda misafir modundasınız. Terapi seanslarınız kaydedilmeyecektir.")

# --- Session State Initialization for Chat ---
if "therapy_chat_session" not in st.session_state:
    st.session_state.therapy_chat_session = None
if "therapy_messages" not in st.session_state:
    st.session_state.therapy_messages = []
if "therapy_started" not in st.session_state:
    st.session_state.therapy_started = False
if "selected_character_therapy" not in st.session_state:
    st.session_state.selected_character_therapy = None

characters = ["Sherlock Holmes", "Firdevs Hanım","Ramiz Dayı","Aksakallı Dede", "İsmail Abi","Burhan Altıntop","Carrie Bradshaw", "Yılmaz"]

# --- Initial Character Selection and Input Form ---
if not st.session_state.therapy_started:
    selected_character = st.selectbox("Karakter Seçimi", characters, key="initial_character_select")
    st.info(f"Seçili karakter: {selected_character}")

    with st.form("initial_therapy_form"):
        user_input = st.text_area("Sorununuzu veya konuşmak istediğiniz konuyu yazın:", key="initial_therapy_input")
        submitted_initial = st.form_submit_button("Terapiye Başla")

    if submitted_initial and user_input:
        if not GEMINI_API_KEY:
            st.error("Gemini API anahtarı bulunamadı. Lütfen .env dosyanızı kontrol edin.")
        else:
            with st.spinner(f"{selected_character} ile terapi başlatılıyor..."):
                st.session_state.therapy_chat_session = start_character_therapy_chat(selected_character)
                if st.session_state.therapy_chat_session:
                    st.session_state.selected_character_therapy = selected_character
                    # Send initial user input and get first response
                    ai_response = st.session_state.therapy_chat_session.send_message(user_input)
                    st.session_state.therapy_messages.append({"role": "user", "content": user_input})
                    st.session_state.therapy_messages.append({"role": "model", "content": ai_response})
                    st.session_state.therapy_started = True
                    # Save initial therapy session for logged-in users
                    if st.session_state.get('logged_in'):
                        add_character_therapy(st.session_state['user_id'], selected_character, user_input, ai_response) # Save initial response
                    st.rerun()
                else:
                    st.error("Sohbet oturumu başlatılamadı. API anahtarını kontrol edin.")

# --- Chat Interface ---
if st.session_state.therapy_started:
    st.markdown("---")
    st.subheader(f"💬 {st.session_state.selected_character_therapy} ile Sohbet")

    # Display chat messages from history
    for message in st.session_state.therapy_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input for new messages
    if prompt := st.chat_input(f"{st.session_state.selected_character_therapy}'a bir şeyler söyleyin..."):
        st.session_state.therapy_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("model"):
            with st.spinner(f"{st.session_state.selected_character_therapy} yanıtlıyor..."):
                ai_response = st.session_state.therapy_chat_session.send_message(prompt)
                st.markdown(ai_response)
                st.session_state.therapy_messages.append({"role": "model", "content": ai_response})

    col_chat_actions = st.columns(2)
    with col_chat_actions[0]:
        if st.button("🔄 Yeni Terapi Başlat"):
            st.session_state.therapy_chat_session = None
            st.session_state.therapy_messages = []
            st.session_state.therapy_started = False
            st.session_state.selected_character_therapy = None
            st.rerun()

# --- History Section (Logged-in users only) ---
if st.session_state.get('logged_in'):
    st.markdown("---")
    st.subheader("🕑 Terapi Geçmişi")
    records = list_character_therapies(st.session_state['user_id'], limit=30)
    if not records:
        st.info("Henüz terapi geçmişiniz yok.")
    else:
        for rec in records:
            with st.expander(f"{rec.created_at.strftime('%d.%m.%Y %H:%M')} - {rec.character}"):
                st.markdown(f"**Sen:** {rec.user_input}")
                st.markdown(f"**{rec.character}:** {rec.ai_response}")
                if st.button(f"❌ Sil", key=f"del_therapy_{rec.id}"):
                    delete_character_therapy(rec.id)
                    st.success("Kayıt silindi!")
                    st.rerun()
