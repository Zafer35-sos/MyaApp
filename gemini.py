import subprocess

def asistan_sohbet(mesaj_gecmisi, yeni_mesaj):
    """
    Sadece ders ve rehberlik konularına cevap veren, 
    diğer konuları nazikçe reddeden rehber öğretmen asistanı.
    """
    # MODELİN KİMLİĞİNİ VE SINIRLARINI BURADA ÇİZİYORUZ
    sistem_talimati = (
        "Sen EduAnaliz sisteminin resmi Rehber Öğretmenisin. "
        "GÖREVİN: Sadece dersler, akademik başarı, arkadaşlık ilişkileri ve okul hayatı hakkında bilgi vermektir. "
        "YASAKLAR: Savaş oyunları, eğlence, siyaset veya ders dışı hobiler hakkında konuşamazsın. "
        "KURAL: Eğer öğrenci ders dışı bir şey sorarsa (örneğin oyunlar), 'Ben sadece derslerin ve okul hayatınla ilgili konularda yardımcı olabilirim, istersen ders çalışma planı yapalım.' şeklinde cevap ver."
    )

    try:
        # Sistem talimatını mesajın başına ekleyerek Ollama'ya gönderiyoruz
        tam_mesaj = f"Sistem: {sistem_talimati}\n\nÖğrenci: {yeni_mesaj}"
        
        komut = ["ollama", "run", "gemma3", tam_mesaj]
        
        islem = subprocess.run(
            komut, 
            capture_output=True, 
            text=True, 
            encoding="utf-8",
            check=True
        )
        
        return islem.stdout.strip()
        
    except subprocess.CalledProcessError as e:
        return f"❌ Ollama hatası: {e}"
    except Exception as e:
        return f"❌ Beklenmedik bir hata: {str(e)}"

def risk_analizi(ortalama_not, devamsizlik, sosyal_skor):
    # Risk analizi zaten akademik olduğu için burası aynı kalabilir
    prompt = (
        f"Rehber öğretmen olarak bu verileri analiz et: "
        f"Not: {ortalama_not}, Devamsızlık: {devamsizlik} gün, Sosyal: {sosyal_skor}/5."
    )
    return asistan_sohbet([], prompt)