import streamlit as st
import database as db
import gemini
import time

st.set_page_config(page_title="EduAnaliz Pro", layout="wide")
db.tablolari_olustur()

if "oturum" not in st.session_state: st.session_state.oturum = False
if "user" not in st.session_state: st.session_state.user = None
if "sohbet_gecmisi" not in st.session_state: st.session_state.sohbet_gecmisi = []

# --- GİRİŞ EKRANI ---
if not st.session_state.oturum:
    b1, orta, b2 = st.columns([1, 1, 1])
    with orta:
        st.markdown("<h2 style='text-align: center;'>🎓 Okul Giriş Sistemi</h2>", unsafe_allow_html=True)
        with st.form("giris"):
            tc = st.text_input("T.C. No")
            sifre = st.text_input("Şifre", type="password")
            if st.form_submit_button("Sisteme Eriş"):
                res = db.kullanici_dogrula(tc, sifre)
                if res:
                    st.session_state.oturum = True
                    st.session_state.user = res
                    st.rerun()
                else: st.error("TC veya Şifre Hatalı!")

# --- ANA PANEL ---
else:
    u = st.session_state.user
    
    with st.sidebar:
        # Profil Kartı
        st.markdown(f"""
            <div style="text-align: center; background-color: #f0f2f6; padding: 15px; border-radius: 15px; border: 1px solid #ddd;">
                <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" width="70">
                <h4 style="margin: 10px 0 0 0;">{u[1]} {u[2]}</h4>
                <small style="color: #666; font-weight: bold;">{u[5]} {f'({u[7]})' if u[7] else ''}</small>
                {f'<br><small style="color: #444;">Sınıf: {u[6]}</small>' if u[6] else ''}
            </div>
        """, unsafe_allow_html=True)
        st.divider()
        
        if u[5] == "Admin":
            menu = st.radio("Yönetim", ["Kullanıcı Kayıt"])
        elif u[5] == "Öğretmen":
            menu = st.radio("Eğitmen", ["Not Girişi", "Öğrenci Listesi"])
        else:
            menu = st.radio("Öğrenci Menüsü", ["Karne", "AI Asistan", "Kaynaklar"])
        
        if st.button("🚪 Güvenli Çıkış", use_container_width=True):
            st.session_state.oturum = False
            st.session_state.user = None
            st.rerun()

    # --- ÖĞRENCİ: AI ASİSTAN (GERİ GELDİ!) ---
    if menu == "AI Asistan":
        st.header("🤖 Akıllı Rehberlik Asistanı")
        st.info("Sistemle veya derslerinle ilgili her şeyi sorabilirsin.")
        
        # Sohbet geçmişini görüntüle
        for m in st.session_state.sohbet_gecmisi:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
        
        # Yeni mesaj girişi
        if prompt := st.chat_input("Derslerin hakkında ne sormak istersin?"):
            st.session_state.sohbet_gecmisi.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("AI Yanıtlıyor..."):
                    yanit = gemini.asistan_sohbet(st.session_state.sohbet_gecmisi, prompt)
                    st.markdown(yanit)
                    st.session_state.sohbet_gecmisi.append({"role": "assistant", "content": yanit})

    # --- ADMIN: KULLANICI KAYIT ---
    elif menu == "Kullanıcı Kayıt":
        st.header("👤 Yeni Kullanıcı Ekle")
        rol_y = st.selectbox("Tanımlanacak Rol", ["Öğrenci", "Öğretmen", "Admin"])
        with st.form("yeni_user_form"):
            c1, c2 = st.columns(2)
            ad_y, soyad_y = c1.text_input("Ad"), c2.text_input("Soyad")
            tc_y, sif_y = c1.text_input("TC No"), c2.text_input("Şifre")
            sinif_y, brans_y = None, None
            if rol_y == "Öğrenci": sinif_y = st.selectbox("Öğrenci Sınıfı", ["9-A", "10-A", "11-B", "12-C"])
            elif rol_y == "Öğretmen": brans_y = st.text_input("Öğretmen Branşı")
            if st.form_submit_button("Kaydı Tamamla"):
                if db.kullanici_ekle(ad_y, soyad_y, tc_y, sif_y, rol_y, sinif_y, brans_y):
                    st.success(f"{ad_y} eklendi!")
                else: st.error("Hata!")

    # --- ÖĞRETMEN: NOT GİRİŞİ ---
    elif menu == "Not Girişi":
        st.header(f"📝 {u[7]} Not Çizelgesi")
        ogrenciler = db.tum_ogrencileri_getir()
        for ogr in ogrenciler:
            with st.expander(f"{ogr[0]} {ogr[1]} - {ogr[3]}"):
                with st.form(key=f"n_f_{ogr[2]}"):
                    v, f = st.number_input("Not", 0, 100), st.number_input("Sözlü", 0, 100)
                    if st.form_submit_button("Kaydet"):
                        db.not_guncelle_veya_ekle(ogr[2], u[7], v, f)
                        st.success("Kaydedildi!")

    # --- ÖĞRENCİ: KARNE ---
    elif menu == "Karne":
        st.header("📊 Akademik Karne")
        notlar = db.ogrenci_notlarini_getir(u[3])
        if notlar:
            karne_data = [{"Ders": n[0], "Vize": n[1], "Final": n[2], "Ortalama": n[1]*0.4+n[2]*0.6} for n in notlar]
            st.table(karne_data)
        else: st.info("Henüz girilmiş bir notunuz yok.")

    # --- ÖĞRENCİ: KAYNAKLAR ---)
    elif menu == "Kaynaklar":
        st.header("📚 Eğitim Kaynakları")
        st.markdown("""
            <div style="background-color: #fff3cd; padding: 30px; border-radius: 15px; border-left: 10px solid #ffc107; text-align: center;">
                <h1 style="color: #856404;">🚧 Yakında Gelecek...</h1>
                <p style="font-size: 18px; color: #856404;">
                    Bu bölümde senin için özel ders notları, PDF kaynaklar ve video eğitimleri paylaşacağız. 
                    <b>Çalışmalarımız devam ediyor!</b>
                </p>
                <img src="https://cdn-icons-png.flaticon.com/512/3588/3588658.png" width="150">
            </div>
        """, unsafe_allow_html=True)
        
        # Ekstra bilgi kartları
        c1, c2 = st.columns(2)
        with c1:
            st.info("📌 **Ders Notları:** Tüm branşlardan özet PDF'ler yüklenecek.")
        with c2:
            st.info("🎥 **Video Arşivi:** Zor konularda hızlı anlatım videoları eklenecek.")


    # Öğretmen Menüsü Altına:
    elif menu == "Öğrenci Analizi":
        st.header("🧠 Yapay Zeka Risk Analizi")
        # Örnek verilerle analiz butonu
        not_v = st.number_input("Öğrenci Ortalaması", 0, 100, 50)
        devam_v = st.number_input("Devamsızlık (Gün)", 0, 30, 5)
        sosyal_v = st.slider("Sosyal Skor", 1, 5, 3)
        
        if st.button("AI Raporu Oluştur"):
            with st.spinner("Analiz ediliyor..."):
                rapor = gemini.risk_analizi(not_v, devam_v, sosyal_v)
                st.markdown(rapor)            