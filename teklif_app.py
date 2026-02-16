import streamlit as st
from fpdf import FPDF
import datetime
import os
import urllib.request
import urllib.parse
import ssl
import time

# --- SSL & DOWNLOAD HELPER ---
try:
    ssl_context = ssl._create_unverified_context()
except AttributeError:
    ssl_context = None

def download_file(url, filename):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, context=ssl_context) as response, open(filename, 'wb') as out_file:
                out_file.write(response.read())
            return True
        except Exception as e:
            print(f"Hata: {filename} indirilemedi ({attempt+1}). {e}")
            time.sleep(1)
    return False

# Logo İndir (Uygulama Başlangıcında)
logo_url = "https://vocaly.com.tr/wp-content/uploads/2026/01/cropped-VOCALY-KARAOKE-Virtual-Logo4-2-136x138.png"
logo_file = "logo.png"
if not os.path.exists(logo_file):
     download_file(logo_url, logo_file)

# --- 1. ENVANTER VE FİYAT LİSTESİ ---
envanter = {
    "45000 Hazır Karaoke Şarkı": {"fiyat": 3000, "link": ""},
    "Smart Vocaly Özellikli Sonsuz Karaoke": {"fiyat": 5000, "link": "https://vocaly.com.tr"},
    "Telefondan Dijital Karaoke İstek Sistemi": {"fiyat": 2000, "link": ""},
    "Karaoke Setup": {"fiyat": 15000, "link": ""},
    "Pioneer RX3 DJ Setup": {"fiyat": 6000, "link": ""},
    "Profesyonel DJ": {"fiyat": 25000, "link": ""},
    "Karaoke Takip Ekranı": {"fiyat": 2500, "link": ""},
    "2 Adet RCF EVOX J8 Hoparlör": {"fiyat": 7000, "link": ""},
    "2 Shure Telsiz Mikrofon": {"fiyat": 4000, "link": ""},
    "6 Kanallı Mackie Mikser": {"fiyat": 2000, "link": ""},
    "2 LED Par Işık": {"fiyat": 1500, "link": ""},
    "2 Işıldak (Efekt Işığı)": {"fiyat": 1500, "link": ""},
    "Nakliye ve Kurulum": {"fiyat": 3500, "link": ""},
    "Müzikli Bingo (Opsiyonel)": {"fiyat": 4000, "link": "https://vocaly.com.tr"},
    "Halk Oylaması (Opsiyonel)": {"fiyat": 3000, "link": "https://vocaly.com.tr"}
}


# --- 1.5 GOOGLE TAKVİM LİNKİ OLUŞTURMA ---
def google_takvim_linki_olustur(musteri_adi, tarih, secilenler):
    base_url = "https://calendar.google.com/calendar/render"
    
    # Tarih Formatı: YYYYMMDD (Başlangıç) / YYYYMMDD (Bitiş - Ertesi Gün)
    start_date = tarih.strftime("%Y%m%d")
    end_date = (tarih + datetime.timedelta(days=1)).strftime("%Y%m%d")
    dates_str = f"{start_date}/{end_date}"
    
    # Açıklama Metni
    details_list = ["Hizmet ve Ekipman Listesi:", ""] + [f"- {h}" for h in secilenler]
    details_text = "\n".join(details_list)
    
    params = {
        "action": "TEMPLATE",
        "text": f"🎤 Vocaly Kurulum: {musteri_adi}",
        "dates": dates_str,
        "details": details_text
    }
    
    query_string = urllib.parse.urlencode(params)
    return f"{base_url}?{query_string}"

# --- 2. PDF OLUŞTURMA FONKSİYONU ---
def teklif_pdf_olustur(musteri_adi, tarih, secilenler, liste_toplami, net_fiyat, indirim, gun_sayisi=0):
    # Font URL'leri
    font_urls = {
        "Roboto-Regular.ttf": "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf",
        "Roboto-Bold.ttf": "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf"
    }

    # SSL context (Sertifika hatasını aşmak için)
    try:
        ssl_context = ssl._create_unverified_context()
    except AttributeError:
        ssl_context = None

    def download_file(url, filename):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(
                    url, 
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                )
                with urllib.request.urlopen(req, context=ssl_context) as response, open(filename, 'wb') as out_file:
                    out_file.write(response.read())
                return True
            except Exception as e:
                # Streamlit loguna yazmak yerine print kullanılabilir, sunucu logunda görünür.
                print(f"Hata: {filename} indirilemedi ({attempt+1}). {e}")
                time.sleep(1)
        return False

    # Fontları İndir
    for font_file, url in font_urls.items():
        if not os.path.exists(font_file):
            download_file(url, font_file)

    # Logo İndir
    logo_url = "https://vocaly.com.tr/wp-content/uploads/2026/01/cropped-VOCALY-KARAOKE-Virtual-Logo4-2-136x138.png"
    logo_file = "logo.png"
    if not os.path.exists(logo_file):
         download_file(logo_url, logo_file)

    # TASARIM AYARLARI (DARK MODE)
    DARK_BG = (0, 0, 0)          # #000000 (Tam Siyah)
    TEXT_WHITE = (224, 224, 224) # #E0E0E0 (Kırık Beyaz)
    ACCENT_COLOR = (255, 75, 43) # #FF4B2B (Mercan/Turuncu - Logo Rengi)
    BOX_BG = (40, 40, 40)        # #282828

    # PDF Sınıfı
    class PDF(FPDF):
        def header(self):
            # Her sayfa arka planını boya
            self.set_fill_color(*DARK_BG)
            self.rect(0, 0, 210, 297, 'F')

    pdf = PDF()
    pdf.add_page()
    
    # Font Ekleme
    try:
        pdf.add_font("Roboto", "", "Roboto-Regular.ttf")
        pdf.add_font("Roboto", "B", "Roboto-Bold.ttf")
        font_name = "Roboto"
    except Exception:
         font_name = "Arial" # Fallback

    # --- İÇERİK ---

    # Logo
    if os.path.exists(logo_file):
        pdf.image(logo_file, x=10, y=8, w=30)
    
    # Header
    pdf.set_y(15)
    pdf.set_font(font_name, 'B', 24)
    pdf.set_text_color(*ACCENT_COLOR)
    pdf.cell(0, 10, txt="TEKLİF DETAYLARI", align='R', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font(font_name, '', 10)
    pdf.set_text_color(200, 200, 200)
    pdf.cell(0, 5, txt="Profesyonel Karaoke & DJ Hizmetleri | Vocaly", align='R', new_x="LMARGIN", new_y="NEXT")
    
    # İletişim Bilgileri
    pdf.set_font(font_name, '', 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 4, txt="www.vocaly.com.tr | info@vocaly.com.tr", align='R', new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(5)

    # Müşteri Bilgileri
    pdf.set_fill_color(*BOX_BG)
    pdf.rect(10, pdf.get_y(), 190, 25, 'F')
    
    pdf.set_y(pdf.get_y() + 5)
    pdf.set_x(15)
    
    pdf.set_font(font_name, 'B', 12)
    pdf.set_text_color(*ACCENT_COLOR)
    pdf.cell(25, 8, txt="Sayın:", align='L')
    pdf.set_font(font_name, '', 12)
    pdf.set_text_color(*TEXT_WHITE)
    pdf.cell(100, 8, txt=f"{musteri_adi}", align='L')
    
    pdf.set_font(font_name, 'B', 12)
    pdf.set_text_color(*ACCENT_COLOR)
    pdf.cell(30, 8, txt="Tarih:", align='R')
    pdf.set_font(font_name, '', 12)
    pdf.set_text_color(*TEXT_WHITE)
    pdf.cell(30, 8, txt=f"{tarih}", align='R', new_x="LMARGIN", new_y="NEXT")

    pdf.ln(15)

    # Hizmetler
    pdf.set_font(font_name, 'B', 14)
    pdf.set_text_color(*ACCENT_COLOR)
    pdf.cell(0, 10, txt="Planlanan Sistem ve Hizmetler", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_draw_color(*ACCENT_COLOR)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    pdf.set_font(font_name, '', 11)
    for i, hizmet in enumerate(secilenler):
        link = envanter.get(hizmet, {}).get("link", "")
        
        if i % 2 == 0:
            pdf.set_fill_color(30, 30, 30) # Daha koyu zebra
            pdf.rect(10, pdf.get_y(), 190, 8, 'F')
            
        pdf.set_x(12)
        pdf.set_text_color(*TEXT_WHITE)
        
        if link:
            pdf.cell(130, 8, txt=f"• {hizmet}")
            pdf.set_text_color(*ACCENT_COLOR)
            pdf.set_font(font_name, 'B', 9)
            pdf.cell(50, 8, txt="[DETAYLAR & GÖRSELLER]", link=link, align='R', new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.cell(0, 8, txt=f"• {hizmet}", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font(font_name, '', 11)

    pdf.ln(10)
    pdf.set_draw_color(100, 100, 100)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    # Finansal Özet Hesaplamaları
    effective_days = gun_sayisi if gun_sayisi > 0 else 1
    
    gunluk_birim_bedel = liste_toplami
    toplam_brut_tutar = gunluk_birim_bedel * effective_days
    net_odenecek_tutar = net_fiyat # UI'dan gelen 'final_net_fiyat' aslında bu
    toplam_indirim = toplam_brut_tutar - net_odenecek_tutar

    # Finansal Tablo Gösterimi
    pdf.set_font(font_name, 'B', 14)
    pdf.set_text_color(*ACCENT_COLOR)
    pdf.cell(0, 10, txt="Finansal Özet", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font(font_name, '', 12)
    pdf.set_text_color(*TEXT_WHITE)
    
    def money_row(label, amount, bold=False, color=TEXT_WHITE, suffix=" ₺"):
        pdf.set_font(font_name, 'B' if bold else '', 12)
        pdf.set_text_color(*color)
        pdf.cell(140, 9, txt=label, border=0)
        
        if suffix == " ₺":
            val = f"{amount:,.2f}{suffix}"
        else:
            val = f"{amount}{suffix}"
        
        pdf.cell(50, 9, txt=val, align='R', border=0, new_x="LMARGIN", new_y="NEXT")

    # 1. Günlük Birim Bedel
    money_row("Günlük Birim Bedel:", gunluk_birim_bedel)
    
    # 2. Toplam Brüt Tutar (+ Gün Sayısı Bilgisi)
    lbl_brut = f"Toplam Brüt Tutar ({effective_days} Gün):" if gun_sayisi > 0 else "Toplam Brüt Tutar:"
    money_row(lbl_brut, toplam_brut_tutar)
    
    # 3. Pakete Özel İndirim
    if toplam_indirim > 0:
        money_row("Pakete Özel İndirim:", -toplam_indirim, color=ACCENT_COLOR)

    pdf.ln(2)
    pdf.set_draw_color(*TEXT_WHITE)
    pdf.line(140, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    # 4. NET ÖDENECEK TUTAR
    # Büyük ve Vurgulu
    pdf.set_x(120)
    pdf.set_font(font_name, 'B', 16)
    pdf.set_text_color(*ACCENT_COLOR)
    pdf.cell(40, 12, txt="NET ÖDENECEK TUTAR:", align='R', border=0)
    pdf.cell(40, 12, txt=f"{net_odenecek_tutar:,.2f} ₺", align='R', border=0, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(15)

    # Genel Şartlar
    pdf.set_font(font_name, 'B', 10)
    pdf.set_text_color(*ACCENT_COLOR)
    pdf.cell(0, 6, txt="GENEL ŞARTLAR:", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font(font_name, '', 8)
    pdf.set_text_color(200, 200, 200)
    terms = [
        "1. Teklif sunulduğu tarihten itibaren 15 gün geçerlidir.",
        "2. Rezervasyon, kapora ödemesi (%20) sonrası kesinleşir.",
        "3. Teknik kurulum için gerekli enerji altyapısı müşteri sorumluluğundadır.",
        "4. İstanbul dışı etkinliklerde konaklama ve iaşe giderleri tarafınıza aittir.",
        "5. Fiyatlara KDV dahil değildir.",
        "6. Operasyonel ekip iaşe ve ulaşım giderleri, etkinlik lokasyonuna göre ayrıca değerlendirilecektir."
    ]
    for term in terms:
        pdf.cell(0, 4, txt=term, new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())

# --- 3. STREAMLIT WEB ARAYÜZÜ ---
if __name__ == "__main__":
    st.set_page_config(page_title="Vocaly Teklif", page_icon="logo.png", layout="centered")

    # --- PWA & MOBİL UYGULAMA AYARLARI ---
    st.markdown("""
        <!-- iOS PWA Meta Etiketleri -->
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <link rel="apple-touch-icon" href="https://raw.githubusercontent.com/scknbspnr-sys/vocaly-teklif/main/logo.png">

        <!-- Mobil Arayüz Optimizasyonu (CSS) -->
        <style>
            /* Streamlit Standart Arayüz Elemanlarını Gizle */
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            .stDeployButton {display:none;}
            
            /* Genel Uygulama Temizliği */
            .block-container {
                padding-top: 1rem !important; /* Üst boşluğu azalt */
                padding-bottom: 2rem !important; /* Alt boşluğu ayarla */
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.image("logo.png", width=150)
    st.title("🎤 Vocaly Teklif Sistemi")

    col1, col2 = st.columns(2)
    with col1:
        musteri_adi = st.text_input("Müşteri / Firma Adı")
    with col2:
        tarih = st.date_input("Etkinlik Tarihi", datetime.date.today())

    st.divider()
    st.subheader("📦 Sunulacak Hizmetleri Seçin")

    secilen_hizmetler = []
    for hizmet, detay in envanter.items():
        if st.checkbox(f"{hizmet} (Liste: {detay['fiyat']} TL)"):
            secilen_hizmetler.append(hizmet)

    liste_toplami = sum(envanter[hizmet]["fiyat"] for hizmet in secilen_hizmetler)

    st.divider()
    st.subheader("💰 Fiyatlandırma ve Akıllı İndirim")

    st.info(f"Seçilen Hizmetlerin Toplam Liste Fiyatı: **{liste_toplami:,.2f} TL**")

    col_fiyat, col_gun = st.columns([2, 1])
    with col_fiyat:
        net_fiyat = st.number_input("Müşteriye Sunulacak NET FİYAT (TL):", min_value=0, value=25000, step=1000)
    with col_gun:
        gun_sayisi = st.number_input("Gün Sayısı (Opsiyonel):", min_value=0, value=0, help="0 bırakırsanız PDF'te görünmez.")

    indirim_orani = liste_toplami - net_fiyat
    if indirim_orani > 0:
        st.success(f"Müşteriye PDF'te gösterilecek olan indirim: **{indirim_orani:,.2f} TL**")
    elif indirim_orani < 0:
        st.warning("Net fiyat liste toplamından yüksek! İndirim yerine fiyat farkı çıkacak.")

    if st.button("📄 Teklifi Oluştur ve İndir", use_container_width=True):
        if not musteri_adi:
            st.error("Lütfen müşteri adını giriniz.")
        elif not secilen_hizmetler:
            st.error("Lütfen en az bir hizmet seçiniz.")
        else:
            if gun_sayisi > 0:
                final_net_fiyat = net_fiyat * gun_sayisi
            else:
                final_net_fiyat = net_fiyat
            
            pdf_bytes = teklif_pdf_olustur(musteri_adi, tarih.strftime("%d.%m.%Y"), secilen_hizmetler, liste_toplami, final_net_fiyat, indirim_orani, gun_sayisi)
            
            st.download_button(
                label="⬇️ PDF'i Cihazına İndir",
                data=pdf_bytes,
                file_name=f"Vocaly_Teklif_{musteri_adi.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            st.balloons()
            
            # Google Takvim Linki Oluştur
            google_url = google_takvim_linki_olustur(musteri_adi, tarih, secilen_hizmetler)
            
            st.link_button(
                label="📅 Google Takvime Ekle",
                url=google_url,
                use_container_width=True
            )