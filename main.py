import streamlit as st
from database import db_manager
from utils import auth

# Page config
st.set_page_config(
    page_title="DreamMind",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db_manager.create_db_and_tables()

# --- Session State Initialization ---
def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "is_guest" not in st.session_state:
        st.session_state.is_guest = False
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = None

# --- UI Components ---
def show_main_content():
    """Displays the main application content after login or for guests."""
    st.sidebar.title(f"Hoş geldin, {st.session_state.username or 'Misafir'}!")
    st.sidebar.markdown("---")

    if st.session_state.logged_in:
        if st.sidebar.button("🚪 Çıkış Yap"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    elif st.session_state.is_guest:
        st.sidebar.warning("Misafir modundasınız. Verilerinizi kaydetmek için lütfen bir hesap oluşturun.")
        if st.sidebar.button("🚀 Kayıt Ol"):
            st.session_state.is_guest = False
            st.rerun()

    st.markdown("<h1 style='text-align: center;'>🌙 DreamMind</h1>", unsafe_allow_html=True)
    st.markdown("### AI destekli rüya analizi ve mental sağlık platformu")
    st.markdown("Sol menüden istediğiniz araca ulaşabilirsiniz.")

    # You can add more content from your original main page here if needed

def show_login_signup_page():
    """Displays the login and signup forms."""
    st.markdown("<h1 style='text-align: center;'>🌙 DreamMind</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        login_tab, signup_tab = st.tabs(["Giriş Yap", "Hesap Oluştur"])

        # --- Login Form ---
        with login_tab:
            with st.form("login_form"):
                username = st.text_input("Kullanıcı Adı", key="login_user")
                password = st.text_input("Şifre", type="password", key="login_pass")
                submitted = st.form_submit_button("Giriş Yap")

                if submitted:
                    user = db_manager.get_user_by_username(username)
                    if user and auth.verify_password(password, user.hashed_password):
                        st.session_state.logged_in = True
                        st.session_state.is_guest = False
                        st.session_state.user_id = user.id
                        st.session_state.username = user.username
                        st.rerun()
                    else:
                        st.error("Kullanıcı adı veya şifre hatalı!")

        # --- Signup Form ---
        with signup_tab:
            with st.form("signup_form"):
                new_username = st.text_input("Kullanıcı Adı", key="signup_user")
                new_password = st.text_input("Şifre", type="password", key="signup_pass")
                confirm_password = st.text_input("Şifre (Tekrar)", type="password", key="signup_pass_confirm")
                signup_submitted = st.form_submit_button("Kayıt Ol")

                if signup_submitted:
                    if not new_username or not new_password:
                        st.error("Kullanıcı adı ve şifre alanları boş bırakılamaz.")
                    elif new_password != confirm_password:
                        st.error("Şifreler eşleşmiyor!")
                    elif db_manager.get_user_by_username(new_username):
                        st.error("Bu kullanıcı adı zaten alınmış!")
                    else:
                        hashed_password = auth.get_password_hash(new_password)
                        new_user = db_manager.add_user(new_username, hashed_password)
                        st.session_state.logged_in = True
                        st.session_state.is_guest = False
                        st.session_state.user_id = new_user.id
                        st.session_state.username = new_user.username
                        st.success("Hesabınız başarıyla oluşturuldu! Yönlendiriliyorsunuz...")
                        st.rerun()

        st.markdown("<p style='text-align: center; margin-top: 2rem;'>veya</p>", unsafe_allow_html=True)
        if st.button("Misafir Olarak Devam Et", use_container_width=True):
            st.session_state.is_guest = True
            st.session_state.logged_in = False
            st.rerun()

# --- Main App Logic ---
init_session_state()

if st.session_state.logged_in or st.session_state.is_guest:
    show_main_content()
else:
    show_login_signup_page()