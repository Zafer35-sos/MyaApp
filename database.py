import sqlite3

def baglan():
    return sqlite3.connect("okul.db", check_same_thread=False)

def tablolari_olustur():
    conn = baglan()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad TEXT, soyad TEXT, tc TEXT UNIQUE, sifre TEXT, rol TEXT,
            sinif TEXT, brans TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ogrenci_tc TEXT,
            ders_adi TEXT,
            vize INTEGER DEFAULT 0,
            final INTEGER DEFAULT 0,
            FOREIGN KEY(ogrenci_tc) REFERENCES kullanicilar(tc)
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM kullanicilar")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO kullanicilar (ad, soyad, tc, sifre, rol) VALUES (?,?,?,?,?)",
                       ("Admin", "Sistem", "000", "admin123", "Admin"))
    conn.commit()
    conn.close()

def kullanici_dogrula(tc, sifre):
    conn = baglan()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM kullanicilar WHERE tc=? AND sifre=?", (tc, sifre))
    user = cursor.fetchone()
    conn.close()
    return user

def kullanici_ekle(ad, soyad, tc, sifre, rol, sinif=None, brans=None):
    try:
        conn = baglan()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO kullanicilar (ad, soyad, tc, sifre, rol, sinif, brans) VALUES (?,?,?,?,?,?,?)",
                       (ad, soyad, tc, sifre, rol, sinif, brans))
        conn.commit()
        conn.close()
        return True
    except: return False

def tum_ogrencileri_getir():
    conn = baglan()
    cursor = conn.cursor()
    cursor.execute("SELECT ad, soyad, tc, sinif FROM kullanicilar WHERE rol='Öğrenci'")
    rows = cursor.fetchall()
    conn.close()
    return rows

def ogrenci_notlarini_getir(tc):
    conn = baglan()
    cursor = conn.cursor()
    cursor.execute("SELECT ders_adi, vize, final FROM notlar WHERE ogrenci_tc=?", (tc,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def not_guncelle_veya_ekle(tc, ders, vize, final):
    conn = baglan()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM notlar WHERE ogrenci_tc=? AND ders_adi=?", (tc, ders))
    res = cursor.fetchone()
    if res:
        cursor.execute("UPDATE notlar SET vize=?, final=? WHERE id=?", (vize, final, res[0]))
    else:
        cursor.execute("INSERT INTO notlar (ogrenci_tc, ders_adi, vize, final) VALUES (?,?,?,?)", (tc, ders, vize, final))
    conn.commit()
    conn.close()