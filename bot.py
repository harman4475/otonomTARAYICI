def resimli_global_post_gonder():
    altyazi = (
        "🚀 <b>GLOBAL M3U & MAC HUB — 24/7 LIVE FEED</b>\n\n"
        "🇹🇷 <b>TR:</b> 7/24 güncel M3U & MAC paylaşımları aktif! Bildirimleri açmayı unutmayın.\n"
        "🇬🇧 <b>EN:</b> 24/7 live M3U & MAC updates active! Turn on notifications.\n"
        "🇩🇪 <b>DE:</b> 24/7 M3U & MAC Updates aktiv! Benachrichtigungen aktivieren.\n"
        "🇮🇹 <b>IT:</b> Aggiornamenti M3U e MAC 24/7 attivi! Attiva le notifiche.\n"
        "🇷🇺 <b>RU:</b> Круглосуточные обновления M3U и MAC активны! Включите уведомления.\n"
        "🇸🇦 <b>AR:</b> تحديثات M3U & MAC نشطة 24/7! قم بتفعيل الإشعارات.\n"
        "🇮🇳 <b>HI:</b> 24/7 लाइव M3U और MAC अपडेट सक्रिय हैं! सूचनाएं चालू करें。\n\n"
        "🌐 <b>Global M3U & MAC Hub</b>"
    )
    
    time.sleep(15)
    
    while True:
        try:
            # Klasördeki uzantısı resim olan ilk dosyayı otomatik bulur
            bulunan_resim = None
            for dosya in os.listdir(BASE_DIR):
                if dosya.lower().endswith(('.png', '.jpg', '.jpeg')):
                    bulunan_resim = os.path.join(BASE_DIR, dosya)
                    break
            
            if not bulunan_resim or not os.path.exists(bulunan_resim):
                print("[!] Uyarı: Klasörde hiçbir görsel bulunamadı! Metin gönderiliyor...")
                telegrama_gonder(altyazi)
            else:
                print(f"[i] Bulunan görsel gönderiliyor: {os.path.basename(bulunan_resim)}")
                url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
                
                with open(bulunan_resim, 'rb') as photo:
                    files = {'photo': photo}
                    data = {
                        'chat_id': CHAT_ID,
                        'caption': altyazi,
                        'parse_mode': 'HTML'
                    }
                    response = requests.post(url, files=files, data=data, timeout=20)
                
                if response.status_code == 200:
                    print("[+] Görsel ve duyuru başarıyla gönderildi.")
                else:
                    print(f"[!] Görsel gönderilemedi. Kod: {response.status_code}")

        except Exception as e:
            print(f"[!] Görsel gönderim döngüsünde hata: {e}")
            
        time.sleep(1800)