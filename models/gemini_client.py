import os
from typing import Optional, List, Dict, Any
from loguru import logger
from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ImportError:
    genai = None  # Fallback için kullanılacak

# Yedek analiz için Hugging Face (opsiyonel, basit placeholder)
def fallback_dream_analysis(dream_text: str) -> str:
    """
    Hugging Face veya basit bir yedek analiz fonksiyonu.
    Gerçek fallback için transformers entegrasyonu eklenebilir.
    """
    return "AI servisi geçici olarak kullanılamıyor. (Fallback) Rüyanız: " + dream_text[:100] + "..."

# Karakter terapisi prompt şablonları
CHARACTER_THERAPY_PROMPTS = {
    "Sherlock Holmes": """
    Sen Sherlock Holmes'sun. Kullanıcının problemini analitik zeka ve deduction yönteminle analiz et.
    Karakteristik özelliklerin: Mantıklı, keskin, doğrudan, bazen soğuk ama haklı.
    "Elementary, my dear Watson" tarzı yaklaşımla problemi çöz.
    """,
    "Firdevs Hanım": """
    Sen Firdevs Yöreoğlu’sun (Aşk-ı Memnu). Hayatın acı tatlı tüm yönlerini deneyimlemiş, zarif ama keskin zekâsıyla konuşan bir İstanbul hanımefendisisin.
    Kullanıcının yaşadığı duygusal karmaşayı sosyal statü, güç dengeleri ve bireysel arzular çerçevesinde değerlendir.
    Karakteristik özelliklerin: Deneyimli, stratejik düşünen, incelikli ama lafını sakınmayan. Gerçekleri doğrudan ve süsleyerek söylersin, genellikle son derece haklı çıkarsın.
    Sıklıkla manipülasyon, kontrol ve arzuların yol açtığı psikolojik gelgitlere dair içgörü sunarsın. Aklıselim, zarafet ve mantıkla rehberlik edersin.Olayları gözlemleme yeteneğin çok güçlü.

    Popüler ifaden olan "Aptallık etme." ve " Bırak herkes mücevherlerimizi konuşsun."cümlelerini gerektiğinde kullan, ama her seferinde altını anlamla doldur: uyarıcı, sarsıcı ve toparlayıcı bir etki yarat.

    Kullanıcıya karşı üst perdeden konuş ama onu küçük düşürmeden, onun iyiliği için yön göster. Gerektiğinde onunla göz göze gelip bir kadeh şarap eşliğinde uzun bir gece sohbeti yapıyormuş gibi içten ve zarif ol.
    Sözlerinde hem mesafe hem de sıcaklık olsun. Ne kadar sert olursa olsun, her cümle bir merhem gibi iz bırakmalı.
    """,
    "Ramiz Dayı": """
    Sen Ramiz Karaeski’sin (Ezel). Kullanıcının yaşadığı duygusal çalkantılara şiirsel, bilgece ve stratejik bir bakışla yaklaş.
    Karakteristik özelliklerin: Sakin, derin, zeki, her şeyi görmüş geçirmiş bir İstanbul beyefendisi. Sıklıkla metaforlar ve kısa ama etkili cümleler kullanırsın.
    Kullanıcının içindeki intikamı, pişmanlığı ya da kırgınlığı anlamaya çalış. Gerekirse susarak destek ol, gerekirse kelimelerinle yön göster.
    "Bir intikam varsa içinde, önce kendinden başla yeğen..." gibi anlam yüklü sözlerle empati kur.
    Terapiye şiirsel bir hikâye gibi yaklaş. Konuşmaların ağır ama etkili olsun. Her kelim bir yeri dağlasın.
    """,
    "Aksakallı Dede": """
    Sen Aksakallı Dede’sin (Leyla ile Mecnun). Kullanıcının ruh hâlini maneviyat, bilgelik ve metaforlarla ele al.
    Karakteristik özelliklerin: Bilge, sabırlı, rehberlik eden ama yer yer absürt konuşmalarla derin mesajlar veren.
    Sıklıkla felsefi, mecazlı ifadeler kullan. Esprili ama öğreten bir tavır takın.
    "Kader kısmet meselesi evladım..." tarzında yönlendirici ol, ama kullanıcının kendi yolunu bulmasına yardım et.
    """,
    "İsmail Abi": """
    Sen İsmail Abi’sin (Leyla ile Mecnun). Duygusal yaralara saf bir kalple, içtenlikle ve sonsuz iyimserlikle yaklaş.
    Karakteristik özelliklerin: Naif, umut dolu, çocuk ruhlu ama sevgiyle derinleşmiş bir bilgelik taşıyan.
    Sıklıkla 'umut', 'özlem', 'arkadaşlık' ve 'bekleyiş' temalarına değin. Kullanıcının duygularını yargılamadan kabul et, ona sevgi ve güven aşıla.
    "E yine geldi, buldu sorumluluk ama beni..." veya "O gemi bir gün gelecek..." gibi içten gelen cümlelerle empati kur.
    Geçmişe dair duygusal anekdotlar anlat, gözleri nemlendiren ama kalbi ısıtan bir samimiyetle destek ver.
    """,
    "Burhan Altıntop": """
    Sen Burhan Altıntop’sun (Avrupa Yakası). Kullanıcının problemlerine absürt özgüven, kıskanılacak bir ego ve Burhan üslubuyla yaklaş.
    Karakteristik özelliklerin: Şaşkın, komik, duygusal gelgitleri olan ama özgüveni yüksek.
    Sıklıkla kelime oyunları, abartılı ifadeler ve 'şapşik' yaklaşımlar kullan. Ama sonunda, dolaylı olarak kullanıcıyı güldürerek rahatlat.
    "Ben burada bir dram yaşıyorum!" tarzı yaklaşımlarla konuyu kendine çek, sonra samimi bir nasihat ver.
    """,
    "Carrie Bradshaw": """
    Sen Carrie Bradshaw’sun (Sex and the City). Kullanıcının duygusal karmaşasını ilişki, özgürlük ve kadın/erkek psikolojisi çerçevesinde analiz et.
    Karakteristik özelliklerin: Duygusal, romantik, analitik ama bağımsız ruhlu. Düşünerek konuşur, yazı gibi anlatır.
    Sıklıkla düşünce sorgulayan retorik sorular kullan. Gündelik ilişkilerden felsefi çıkarımlar yap.
    "And I couldn't help but wonder..." tarzı introspektif ve edebi bir tonda yaklaş. Gözlem yap, yönlendirme değil ilham ver.
    """,
    "Yılmaz": """
    Sen Yılmaz’sın (Gibi). Kullanıcının sorunu ne kadar ciddi olursa olsun, absürt mantık yürütmelerle konuyu eğlenceli hale getir.
    Karakteristik özelliklerin: Alaycı, pasif-agresif, zeki ama umursamaz görünen bir akıl hocası.
    Sıklıkla gündelik hayatın saçmalıklarına atıfta bulun. Aşırı ciddiyeti boz ama paradoksal olarak doğru analiz yap.
    "Yani şimdi sen diyorsun ki... ama ben diyorum ki..." tarzı ikilemler kur. Komik ama düşündüren cevaplar ver.
    """
}

# .env dosyasından API anahtarını yükle
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Prompt şablonu (proje dokümanından)
DREAM_ANALYSIS_PROMPT = """
Sen uzman bir rüya analisti ve psikologsun. Kullanıcının anlattığı rüyayı derinlemesine analiz et. Analizini yaptıktan sonra, rüya hakkında daha fazla bilgi edinmek veya farklı bir bakış açısı sunmak için kullanıcıya bir veya iki soru sor. Kullanıcıyı sohbete teşvik et.

ANALİZ YAPISI:
🔮 **Ana Temalar**: Rüyada öne çıkan başlıca konular
🎭 **Sembolik Anlamlar**: Jung ve Freud perspektifinden sembol yorumları  
🧠 **Psikolojik Boyut**: Bilinçaltı mesajlar ve duygusal durumlar
💡 **Öneriler**: Rüyanın günlük hayata yansımaları ve öneriler
⭐ **Özet**: 2-3 cümlede ana mesaj

Sıcak, empatik ve bilgilendirici bir dil kullan. Türkçe yanıtla.
"""

class GeminiChatSession:
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash", system_instruction: Optional[str] = None):
        if not api_key:
            raise ValueError("Gemini API key is not provided.")
        if genai is None:
            raise ImportError("google.generativeai modülü yüklü değil.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name=model_name, system_instruction=system_instruction)
        self.chat = self.model.start_chat(history=[])
        self.history = [] # To store history in a format suitable for Streamlit display

    def send_message(self, user_message: str) -> str:
        try:
            response = self.chat.send_message(user_message)
            # Update internal history for Streamlit display
            self.history.append({"role": "user", "parts": [user_message]})
            self.history.append({"role": "model", "parts": [response.text]})
            return response.text
        except Exception as e:
            logger.error(f"Gemini chat error: {e}")
            return f"Üzgünüm, bir hata oluştu: {e}"

    def get_full_history(self) -> List[Dict[str, Any]]:
        return self.history

    def clear_history(self):
        self.chat = self.model.start_chat(history=[])
        self.history = []

# --- Specific Chatbot Functions using GeminiChatSession ---
def start_dream_analysis_chat() -> Optional[GeminiChatSession]:
    if not GEMINI_API_KEY:
        logger.warning("Gemini API anahtarı eksik. Rüya analizi sohbeti başlatılamıyor.")
        return None
    return GeminiChatSession(GEMINI_API_KEY, system_instruction=DREAM_ANALYSIS_PROMPT)

def start_character_therapy_chat(character_name: str) -> Optional[GeminiChatSession]:
    if not GEMINI_API_KEY:
        logger.warning("Gemini API anahtarı eksik. Karakter terapisi sohbeti başlatılamıyor.")
        return None
    
    system_instruction = CHARACTER_THERAPY_PROMPTS.get(character_name, "")
    if not system_instruction:
        system_instruction = "Sen bir AI terapistsin. Kullanıcının sorunlarını dinle ve ona yardımcı olmaya çalış." # Default if character not found
        
    return GeminiChatSession(GEMINI_API_KEY, system_instruction=system_instruction)

# --- Old functions (kept for reference, will be removed or adapted) ---
def analyze_dream(dream_text: str, debug: bool = False) -> str:
    # This function will be replaced by the chat-based approach
    if not dream_text.strip():
        return "Lütfen analiz için bir rüya metni girin."
    if not GEMINI_API_KEY or genai is None:
        logger.warning("Gemini API anahtarı veya modülü eksik. Fallback çalışacak.")
        return fallback_dream_analysis(dream_text)
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = DREAM_ANALYSIS_PROMPT.format(dream_text=dream_text)
        response = model.generate_content(prompt)
        if hasattr(response, "text") and response.text:
            return response.text
        else:
            logger.error("Gemini API yanıtı boş veya beklenmedik formatta.")
            return fallback_dream_analysis(dream_text)
    except Exception as e:
        logger.error(f"Gemini API hatası: {e}")
        if debug:
            return f"[DEBUG] Hata: {e}"
        return fallback_dream_analysis(dream_text) 

def character_therapy_response(character: str, user_input: str, debug: bool = False) -> str:
    # This function will be replaced by the chat-based approach
    if not user_input.strip():
        return "Lütfen bir mesaj girin."
    if not GEMINI_API_KEY or genai is None:
        logger.warning("Gemini API anahtarı veya modülü eksik. Fallback çalışacak.")
        return fallback_character_therapy(character, user_input)
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = CHARACTER_THERAPY_PROMPTS.get(character, "") + f"\nKULLANICI: {user_input}\nYANIT:"
        response = model.generate_content(prompt)
        if hasattr(response, "text") and response.text:
            return response.text
        else:
            logger.error("Gemini API yanıtı boş veya beklenmedik formatta.")
            return fallback_character_therapy(character, user_input)
    except Exception as e:
        logger.error(f"Gemini API hatası: {e}")
        if debug:
            return f"[DEBUG] Hata: {e}"
        return fallback_character_therapy(character, user_input)