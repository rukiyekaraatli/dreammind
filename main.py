import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="DreamMind",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">🌙 DreamMind</h1>', unsafe_allow_html=True)
    st.markdown("### AI destekli rüya analizi ve mental sağlık platformu")
    
    # Sidebar
    st.sidebar.title("🎯 Navigasyon")
    st.sidebar.markdown("---")
    st.sidebar.info("Çok yakında: Rüya Analizi, Mood Tracker, Karakter Terapisi!")
    
    # Main content
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.button("🔮 Rüya Analizi")
    
    with col2:
        st.button("😊 Mood Tracker")
    
    with col3:
        st.button("💬 Karakter Terapisi")
    
    # Statistics
    st.markdown("---")
    st.subheader("📊 Platform İstatistikleri")
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    metric_col1.metric("Analiz Edilen Rüya", "0", "0")
    metric_col2.metric("Aktif Kullanıcı", "1", "1")
    metric_col3.metric("Terapi Seansı", "0", "0")
    metric_col4.metric("Mood Kayıtları", "0", "0")

if __name__ == "__main__":
    main()
