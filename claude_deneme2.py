"""PAZARLIK ZAMANI v2 - Bütçe, rastgele satıcı, ürün ve gizli kusur
Kurulum: python -m pip install customtkinter
Çalıştırma: python pazarlik_v2.py
"""
import json
import os
import random
import re

import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Kayıt dosyası, oyun dosyasının yanında durur (hangi klasörden açarsan aç aynı yer).
KAYIT_DOSYASI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kayit.json")
MAX_SABIR = 3

# ----------------------------------------------------------------------------
# OYUN AYARLARI: Tüm metinler, karakterler, ürünler, renkler ve emojiler burada.
# Kod bilmeden burayı değiştirerek oyunu istediğin gibi değiştirebilirsin.
#
# butce_orani: Cebindeki para, ürünün etiket fiyatının bu oranları arasında olur.
#   (0.95, 0.975) -> 10.000 TL'lik ürün için 9.500 - 9.750 TL cebinde olur.
#   Oran ne kadar düşükse, o satıcıyla pazarlık o kadar zorunlu olur.
# esneklik: Satıcının ne kadar kolay indirim yaptığı (1.0 = kolay, 0.7 = inatçı).
# ----------------------------------------------------------------------------
OYUN_AYARLARI = {
    "saticilar": [
        {"ad": "İnatçı Kazım", "emoji": "😠", "renk": "#4a1f1f", "esneklik": 0.7,
         "butce_orani": (0.90, 0.94),
         "karsilama": "Ne bakmıştın? Alıcıysan konuşalım, vaktim yok."},
        {"ad": "Tatlı Dilli Ayşe", "emoji": "😊", "renk": "#1c4a2b", "esneklik": 1.0,
         "butce_orani": (0.95, 0.975),
         "karsilama": "Hoş geldin! Sana pırıl pırıl bir cihaz vereyim, ne dersin?"},
        {"ad": "Teknoloji Kurdu Mert", "emoji": "🤓", "renk": "#2a2f5c", "esneklik": 0.85,
         "butce_orani": (0.92, 0.96),
         "karsilama": "Elimde tam sana göre donanımlar var. Şuna bir bak."},
    ],
    "urunler": [
        {"ad": "G-Phone X", "fiyat": 10000, "dip_fiyat": 8000},
        {"ad": "Samny Z Katlanabilir", "fiyat": 15000, "dip_fiyat": 13000},
        {"ad": "Akıllı Gözlük Prototipi (Orange Pi Modüllü)", "fiyat": 4500, "dip_fiyat": 3200},
    ],
    "kusurlar": [
        "Bataryası çok hızlı bitiyor.",
        "Ekranda ölü pikseller var.",
        "Cihazın yazılımı kilitli.",
        None,  # None = kusursuz cihaz
        None,
    ],
    # Kusuru bulursan satıcının inebileceği en düşük fiyat bu kadar düşer.
    "kusur_indirimi": 1000,
    "sahneler": {
        "giris": ("🏪", "#1b2a40"),
        "inceleme_kusurlu": ("🧐", "#4a3f12"),
        "inceleme_temiz": ("✨", "#1c4a2b"),
        "pazarlik_basarili": ("🤔", "#33284f"),
        "pazarlik_olmaz": ("😤", "#4a1f1f"),
        "para_yetmiyor": ("😬", "#4a3f12"),
    },
    "sonlar": {
        "son_1": {"baslik": "Kusursuz Kazanç", "emoji": "🤝", "renk": "#14532d",
                  "metin": "Tertemiz cihazı harika bir pazarlıkla aldın!"},
        "son_2": {"baslik": "Kazıklandın", "emoji": "💸", "renk": "#5b1a1a",
                  "metin": "Cihaza değerinden çok daha fazla para verdin."},
        "son_3": {"baslik": "Kör Alışveriş", "emoji": "😵", "renk": "#5b1a1a",
                  "metin": "İncelemeden aldın! Eve gidince cihazdaki gizli kusuru fark ettin. Geçmiş olsun."},
        "son_4": {"baslik": "Kovuldun!", "emoji": "🤬", "renk": "#7a1f1f",
                  "metin": "Satıcının sabrını çok zorladın, seni dükkandan kovdu."},
        "son_5": {"baslik": "Vazgeçtin", "emoji": "🚶", "renk": "#2b3445",
                  "metin": "Alışverişten vazgeçip dükkandan ayrıldın."},
        "son_6": {"baslik": "Uyanık Alıcı", "emoji": "😎", "renk": "#14532d",
                  "metin": "Kusuru fark edip fiyatı iyice kırdın ve yedek parça niyetine aldın!"},
        "son_7": {"baslik": "Yetmeyen Bütçe", "emoji": "👛", "renk": "#3b2f4a",
                  "metin": "Pazarlık yaptın ama fiyatı cebindeki paraya indiremedin. Eli boş döndün."},
    },
}


def tl(tutar):
    """8500 -> '8.500 TL'"""
    return f"{tutar:,}".replace(",", ".") + " TL"


class PazarlikOyunu(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pazarlık Zamanı v2")
        self.geometry("1000x740")
        self.minsize(880, 700)
        self.configure(fg_color="#0b1220")
        self.gecmis_pencere = None

        self.kayit_yukle()
        self.arayuz_olustur()
        self.yeni_oyun()

    # ------------------------------------------------------------------ kayıt
    def kayit_yukle(self):
        kayit = {"kesfedilen_sonlar": [], "oyun_sayisi": 0, "en_cok_tasarruf": 0}
        try:
            with open(KAYIT_DOSYASI, "r", encoding="utf-8") as f:
                veri = json.load(f)
            if isinstance(veri, dict):
                kayit.update(veri)
        except (OSError, ValueError):
            pass  # dosya yok veya bozuk: sıfırdan başla
        if not isinstance(kayit["kesfedilen_sonlar"], list):
            kayit["kesfedilen_sonlar"] = []
        self.kayit = kayit

    def kaydet(self):
        try:
            with open(KAYIT_DOSYASI, "w", encoding="utf-8") as f:
                json.dump(self.kayit, f, ensure_ascii=False, indent=4)
        except OSError:
            pass  # kaydedilemese de oyun devam etsin

    # ----------------------------------------------------------------- arayüz
    def arayuz_olustur(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # Sol panel: sahne, diyalog, butonlar
        sol = ctk.CTkFrame(self, fg_color="#111c2e", corner_radius=18)
        sol.grid(row=0, column=0, padx=(18, 9), pady=18, sticky="nsew")
        sol.grid_columnconfigure(0, weight=1)
        sol.grid_rowconfigure(1, weight=1)

        self.sahne = ctk.CTkFrame(sol, fg_color="#1b2a40", corner_radius=14, height=170)
        self.sahne.grid(row=0, column=0, padx=18, pady=(18, 8), sticky="ew")
        self.sahne.grid_propagate(False)
        self.sahne.grid_columnconfigure(0, weight=1)
        self.sahne.grid_rowconfigure(0, weight=1)
        self.emoji_label = ctk.CTkLabel(self.sahne, text="🏪", font=ctk.CTkFont(size=72))
        self.emoji_label.grid(row=0, column=0, pady=(8, 0))
        self.sahne_yazi = ctk.CTkLabel(self.sahne, text="", font=ctk.CTkFont(size=14, weight="bold"),
                                       text_color="#dbe6f5")
        self.sahne_yazi.grid(row=1, column=0, pady=(0, 10))

        self.log = ctk.CTkTextbox(sol, wrap="word", corner_radius=12, fg_color="#0b1424",
                                  text_color="#e4ebf5", font=ctk.CTkFont(size=14),
                                  border_width=1, border_color="#25354d")
        self.log.grid(row=1, column=0, padx=18, pady=8, sticky="nsew")
        self.log.configure(state="disabled")

        butonlar = ctk.CTkFrame(sol, fg_color="transparent")
        butonlar.grid(row=2, column=0, padx=18, pady=(8, 18), sticky="ew")
        butonlar.grid_columnconfigure((0, 1), weight=1)

        self.btn_incele = ctk.CTkButton(butonlar, text="🔍  Cihazı İncele", height=40, command=self.incele)
        self.btn_pazarlik = ctk.CTkButton(butonlar, text="💬  Pazarlık Yap", height=40, command=self.pazarlik_yap)
        self.btn_satin_al = ctk.CTkButton(butonlar, text="💰  Satın Al", height=40, command=self.satin_al,
                                          fg_color="#16a34a", hover_color="#15803d")
        self.btn_ayril = ctk.CTkButton(butonlar, text="🚶  Çıkış Yap", height=40, command=self.ayril,
                                       fg_color="#26364d", hover_color="#344964")
        self.btn_incele.grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        self.btn_pazarlik.grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        self.btn_satin_al.grid(row=1, column=0, padx=4, pady=4, sticky="ew")
        self.btn_ayril.grid(row=1, column=1, padx=4, pady=4, sticky="ew")

        # Kendi teklifini yazma alanı
        self.teklif_giris = ctk.CTkEntry(butonlar, height=40, placeholder_text="Kendi teklifini yaz (örn. 9250)")
        self.teklif_giris.grid(row=2, column=0, padx=4, pady=4, sticky="ew")
        self.teklif_giris.bind("<Return>", lambda olay: self.teklif_ver())
        self.btn_teklif = ctk.CTkButton(butonlar, text="📨  Teklif Ver", height=40, command=self.teklif_ver,
                                        fg_color="#7c3aed", hover_color="#6d28d9")
        self.btn_teklif.grid(row=2, column=1, padx=4, pady=4, sticky="ew")

        self.btn_yeniden = ctk.CTkButton(butonlar, text="🔄  Yeniden Oyna", height=40,
                                         command=self.yeni_oyun, fg_color="#0ea5e9", hover_color="#0284c7")
        self.btn_yeniden.grid(row=3, column=0, columnspan=2, padx=4, pady=4, sticky="ew")
        self.btn_yeniden.grid_remove()

        # Sağ panel: bilgi kartları
        sag = ctk.CTkFrame(self, fg_color="#111c2e", corner_radius=18)
        sag.grid(row=0, column=1, padx=(9, 18), pady=18, sticky="nsew")
        sag.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(sag, text="ALIŞVERİŞ ÖZETİ", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#8da4c4").grid(row=0, column=0, padx=18, pady=(18, 10), sticky="w")
        self.satici_kart = self.kart(sag, 1, "Satıcı")
        self.urun_kart = self.kart(sag, 2, "Ürün")
        self.para_kart = self.kart(sag, 3, "Cebindeki para")
        self.fiyat_kart = self.kart(sag, 4, "Güncel fiyat")
        self.fark_kart = self.kart(sag, 5, "Bütçe durumu")
        self.sabir_kart = self.kart(sag, 6, "Satıcının sabrı")
        self.durum_kart = self.kart(sag, 7, "Cihaz durumu")
        self.gecmis_ozet = ctk.CTkLabel(sag, text="", text_color="#9fb0c8", font=ctk.CTkFont(size=12))
        self.gecmis_ozet.grid(row=8, column=0, padx=18, pady=(10, 4), sticky="w")
        ctk.CTkButton(sag, text="🏆  Sonlarım", command=self.sonlari_goster,
                      fg_color="#ca8a04", hover_color="#a16207").grid(row=9, column=0, padx=16, pady=(4, 16),
                                                                       sticky="ew")

    def kart(self, parent, satir, baslik):
        cerceve = ctk.CTkFrame(parent, fg_color="#172439", corner_radius=12)
        cerceve.grid(row=satir, column=0, padx=15, pady=4, sticky="ew")
        ctk.CTkLabel(cerceve, text=baslik, text_color="#9fb0c8",
                     font=ctk.CTkFont(size=12)).pack(anchor="w", padx=12, pady=(8, 0))
        etiket = ctk.CTkLabel(cerceve, text="-", font=ctk.CTkFont(size=16, weight="bold"),
                              wraplength=280, justify="left")
        etiket.pack(anchor="w", padx=12, pady=(0, 8))
        return etiket

    def say(self, kim, metin):
        self.log.configure(state="normal")
        self.log.insert("end", f"{kim}\n{metin}\n\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def sahne_ayarla(self, emoji, renk, yazi=""):
        self.sahne.configure(fg_color=renk)
        self.emoji_label.configure(text=emoji)
        self.sahne_yazi.configure(text=yazi)

    def durum_guncelle(self):
        self.satici_kart.configure(text=self.satici["ad"])
        self.urun_kart.configure(text=self.urun["ad"])
        self.para_kart.configure(text=tl(self.butce))
        self.fiyat_kart.configure(text=tl(self.mevcut_fiyat))

        fark = self.mevcut_fiyat - self.butce
        if fark > 0:
            self.fark_kart.configure(text=f"⚠️ Bütçeni {tl(fark)} aşıyor", text_color="#f87171")
        else:
            self.fark_kart.configure(text=f"✅ Bütçene uygun ({tl(-fark)} artar)", text_color="#4ade80")

        self.sabir_kart.configure(text="❤️" * self.sabir + "🖤" * (MAX_SABIR - self.sabir))
        if not self.incelendi:
            durum = "Henüz incelenmedi"
        elif self.kusur:
            durum = f"Kusur: {self.kusur}"
        else:
            durum = "Kusursuz ✅"
        self.durum_kart.configure(text=durum)
        toplam = len(OYUN_AYARLARI["sonlar"])
        bulunan = len(self.kayit["kesfedilen_sonlar"])
        self.gecmis_ozet.configure(text=f"Keşfedilen sonlar: {bulunan}/{toplam}")

    def butonlari_ayarla(self, aktif):
        durum = "normal" if aktif else "disabled"
        for btn in (self.btn_incele, self.btn_pazarlik, self.btn_satin_al, self.btn_ayril, self.btn_teklif):
            btn.configure(state=durum)
        self.teklif_giris.configure(state=durum)

    # ------------------------------------------------------------------ oyun
    def taban_fiyat(self):
        """Satıcının inebileceği en düşük fiyat. Kusuru bulduysan daha da düşer."""
        taban = self.urun["dip_fiyat"]
        if self.incelendi and self.kusur:
            taban -= OYUN_AYARLARI["kusur_indirimi"]
        return taban

    def yeni_oyun(self):
        self.satici = random.choice(OYUN_AYARLARI["saticilar"])
        self.urun = random.choice(OYUN_AYARLARI["urunler"])
        self.kusur = random.choice(OYUN_AYARLARI["kusurlar"])
        self.mevcut_fiyat = self.urun["fiyat"]
        oran = random.uniform(*self.satici["butce_orani"])
        self.butce = round(self.urun["fiyat"] * oran / 50) * 50
        self.sabir = MAX_SABIR
        self.incelendi = False
        self.oyun_bitti = False

        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self.btn_yeniden.grid_remove()
        self.butonlari_ayarla(True)
        self.teklif_giris.delete(0, "end")

        self.sahne_ayarla(self.satici["emoji"], self.satici["renk"], self.satici["ad"])
        self.say("Anlatıcı", f"Dükkana girdin. {self.satici['ad']} tezgahta duruyor.")
        self.say(self.satici["ad"], self.satici["karsilama"])
        self.say("Anlatıcı", f"Tezgahtaki ürün: {self.urun['ad']}\n"
                             f"İstenen fiyat: {tl(self.mevcut_fiyat)}\n"
                             f"Cebindeki para: {tl(self.butce)}")
        if self.mevcut_fiyat > self.butce:
            self.say("Anlatıcı", f"💡 Fiyat bütçeni {tl(self.mevcut_fiyat - self.butce)} aşıyor. "
                                 "Pazarlık yapmadan alamazsın!")
        self.durum_guncelle()

    def sabir_harca(self):
        """Her pazarlık veya teklif satıcının sabrını azaltır. Sabır bittiyse oyun biter."""
        if self.sabir <= 0:
            self.say("Sen", "Bir indirim daha yapabilir misiniz?")
            self.sonlandir("son_4")
            return False
        self.sabir -= 1
        return True

    def sabir_uyarisi(self):
        if self.sabir == 0 and not self.oyun_bitti:
            self.say("Anlatıcı", "⚠️ Satıcının sabrı tükendi. Bir kez daha pazarlık yaparsan seni kovabilir!")

    def incele(self):
        if self.oyun_bitti or self.incelendi:
            return
        self.incelendi = True
        self.btn_incele.configure(state="disabled")
        self.say("Sen", "Cihazı dikkatlice inceleyebilir miyim?")
        if self.kusur:
            emoji, renk = OYUN_AYARLARI["sahneler"]["inceleme_kusurlu"]
            self.say("İnceleme sonucu", f"Dikkatli bakınca fark ettin: {self.kusur}\n"
                                        "Bunu pazarlıkta kullanabilirsin!")
            self.sahne_ayarla(emoji, renk, "Bir sorun buldun!")
        else:
            emoji, renk = OYUN_AYARLARI["sahneler"]["inceleme_temiz"]
            self.say("İnceleme sonucu", "Cihazın dış görünüşü ve donanımı sapasağlam. Tertemiz.")
            self.sahne_ayarla(emoji, renk, "Cihaz temiz")
        self.durum_guncelle()

    def pazarlik_yap(self):
        if self.oyun_bitti:
            return
        if not self.sabir_harca():
            return
        self.say("Sen", random.choice([
            "Bütçem kısıtlı, biraz indirim yapabilir misiniz?",
            "Bu fiyat biraz yüksek kaldı, ne dersiniz?",
            "Peşin ödeyeceğim, bir indirim olur mu?",
        ]))

        taban = self.taban_fiyat()
        if self.mevcut_fiyat <= taban:
            self.say(self.satici["ad"], f"Zararına satış yapamam! Son fiyat {tl(self.mevcut_fiyat)}.")
            emoji, renk = OYUN_AYARLARI["sahneler"]["pazarlik_olmaz"]
            self.sahne_ayarla(emoji, renk, "Daha fazla inmiyor")
        else:
            indirim = round(random.randint(300, 1000) * self.satici["esneklik"] / 50) * 50
            if self.incelendi and self.kusur:
                indirim += round(random.randint(800, 1500) / 50) * 50
            self.mevcut_fiyat = max(taban, self.mevcut_fiyat - indirim)
            self.say(self.satici["ad"], f"Peki, senin için {tl(self.mevcut_fiyat)} olsun. Daha da inmem!")
            emoji, renk = OYUN_AYARLARI["sahneler"]["pazarlik_basarili"]
            self.sahne_ayarla(emoji, renk, "Fiyat düştü")

        self.sabir_uyarisi()
        self.durum_guncelle()

    def teklif_ver(self):
        """Oyuncu kendi fiyatını yazar. Satıcı kabul eder, karşı teklif yapar ya da sinirlenir."""
        if self.oyun_bitti:
            return
        rakam = re.sub(r"\D", "", self.teklif_giris.get())
        if not rakam:
            self.say("Anlatıcı", "Geçerli bir sayı yaz. Örnek: 9250")
            return
        teklif = int(rakam)
        if teklif >= self.mevcut_fiyat:
            self.say("Anlatıcı", f"Teklifin ({tl(teklif)}) güncel fiyattan düşük değil, bu bir indirim sayılmaz.")
            return
        self.teklif_giris.delete(0, "end")
        if not self.sabir_harca():
            return

        self.say("Sen", f"{tl(teklif)} vereyim, ne dersiniz?")
        taban = self.taban_fiyat()
        # Satıcı, tabanın biraz üstünü kabul eder. İnatçı satıcıların eşiği daha yüksektir.
        esik = taban + round(400 * (2 - self.satici["esneklik"]) / 50) * 50

        if teklif >= esik:
            self.mevcut_fiyat = teklif
            self.say(self.satici["ad"], f"Tamam, {tl(teklif)} olsun. El sıkışalım!")
            emoji, renk = OYUN_AYARLARI["sahneler"]["pazarlik_basarili"]
            self.sahne_ayarla(emoji, renk, "Teklifin kabul edildi")
        elif teklif >= taban:
            karsi = max(esik, round((teklif + self.mevcut_fiyat) / 2 / 50) * 50)
            if karsi < self.mevcut_fiyat:
                self.mevcut_fiyat = karsi
                self.say(self.satici["ad"], f"O kadar olmaz, ama {tl(karsi)} diyebilirim.")
                emoji, renk = OYUN_AYARLARI["sahneler"]["pazarlik_basarili"]
                self.sahne_ayarla(emoji, renk, "Karşı teklif geldi")
            else:
                self.say(self.satici["ad"], f"Bundan aşağı inemem! Fiyat {tl(self.mevcut_fiyat)}.")
                emoji, renk = OYUN_AYARLARI["sahneler"]["pazarlik_olmaz"]
                self.sahne_ayarla(emoji, renk, "Daha fazla inmiyor")
        else:
            self.say(self.satici["ad"], "Bu fiyata mı? Benimle dalga mı geçiyorsun!")
            emoji, renk = OYUN_AYARLARI["sahneler"]["pazarlik_olmaz"]
            self.sahne_ayarla(emoji, renk, "Teklifin çok düşük")

        self.sabir_uyarisi()
        self.durum_guncelle()

    def satin_al(self):
        if self.oyun_bitti:
            return
        if self.mevcut_fiyat > self.butce:
            self.say("Anlatıcı", f"💳 Cebindeki para ({tl(self.butce)}) yetmiyor! "
                                 f"Fiyat {tl(self.mevcut_fiyat)}. Önce fiyatı düşürmelisin.")
            emoji, renk = OYUN_AYARLARI["sahneler"]["para_yetmiyor"]
            self.sahne_ayarla(emoji, renk, "Paran yetmiyor")
            return

        self.say("Sen", f"Tamam, {tl(self.mevcut_fiyat)}'ye alıyorum.")
        if self.kusur and not self.incelendi:
            self.sonlandir("son_3", satin_alindi=True)
        elif self.kusur:
            # Kusuru bildin: ancak taban fiyata yakın alırsan akıllıca bir alışveriştir.
            if self.mevcut_fiyat <= self.urun["dip_fiyat"]:
                self.sonlandir("son_6", satin_alindi=True)
            else:
                self.sonlandir("son_2", satin_alindi=True)
        elif self.mevcut_fiyat <= self.urun["dip_fiyat"] + 500:
            self.sonlandir("son_1", satin_alindi=True)
        else:
            self.sonlandir("son_2", satin_alindi=True)

    def ayril(self):
        if self.oyun_bitti:
            return
        self.say("Sen", "Teşekkürler, şimdilik almayacağım.")
        pazarlik_denendi = self.sabir < MAX_SABIR
        if pazarlik_denendi and self.mevcut_fiyat > self.butce:
            self.sonlandir("son_7")  # fiyatı bütçeye indiremedi
        else:
            self.sonlandir("son_5")

    def sonlandir(self, son_id, satin_alindi=False):
        self.oyun_bitti = True
        self.butonlari_ayarla(False)
        son = OYUN_AYARLARI["sonlar"][son_id]
        self.sahne_ayarla(son["emoji"], son["renk"], son["baslik"])

        self.say(f"🏁 OYUN BİTTİ: {son['baslik']}", son["metin"])

        if satin_alindi:
            tasarruf = self.urun["fiyat"] - self.mevcut_fiyat
            self.say("SONUÇ", f"Ödediğin: {tl(self.mevcut_fiyat)}\n"
                              f"Kalan paran: {tl(self.butce - self.mevcut_fiyat)}\n"
                              f"Etiket fiyatına göre fark: {tl(tasarruf)}")
            if son_id in ("son_1", "son_6") and tasarruf > self.kayit["en_cok_tasarruf"]:
                self.kayit["en_cok_tasarruf"] = tasarruf
                self.say("🏅 REKOR", f"En yüksek tasarrufun: {tl(tasarruf)}")
        else:
            self.say("SONUÇ", f"Cebindeki para: {tl(self.butce)} (hiç harcamadın)")

        self.kayit["oyun_sayisi"] += 1
        if son_id not in self.kayit["kesfedilen_sonlar"]:
            self.kayit["kesfedilen_sonlar"].append(son_id)
            toplam = len(OYUN_AYARLARI["sonlar"])
            self.say("🔓 YENİ SON AÇILDI", f"{son['baslik']}  ({len(self.kayit['kesfedilen_sonlar'])}/{toplam})")
        self.kaydet()
        self.durum_guncelle()
        self.btn_yeniden.grid()

    # ----------------------------------------------------------- sonlarım
    def sonlari_goster(self):
        if self.gecmis_pencere is not None and self.gecmis_pencere.winfo_exists():
            self.gecmis_pencere.destroy()  # güncel bilgiyle yeniden aç

        pencere = ctk.CTkToplevel(self)
        pencere.title("Sonlarım")
        pencere.geometry("420x560")
        pencere.configure(fg_color="#0b1220")
        self.gecmis_pencere = pencere

        toplam = len(OYUN_AYARLARI["sonlar"])
        bulunan = len(self.kayit["kesfedilen_sonlar"])
        ctk.CTkLabel(pencere, text=f"🏆 Keşfedilen Sonlar ({bulunan}/{toplam})",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(padx=20, pady=(20, 10), anchor="w")

        for son_id, son in OYUN_AYARLARI["sonlar"].items():
            bulundu = son_id in self.kayit["kesfedilen_sonlar"]
            satir = ctk.CTkFrame(pencere, fg_color="#172439", corner_radius=10)
            satir.pack(fill="x", padx=20, pady=4)
            baslik = f"✅ {son['emoji']}  {son['baslik']}" if bulundu else "🔒  ???"
            ctk.CTkLabel(satir, text=baslik, font=ctk.CTkFont(size=15, weight="bold")).pack(
                anchor="w", padx=12, pady=(8, 0 if bulundu else 8))
            if bulundu:
                ctk.CTkLabel(satir, text=son["metin"], wraplength=350, justify="left",
                             text_color="#b9c8dc").pack(anchor="w", padx=12, pady=(0, 8))

        istatistik = (f"Oynanan oyun: {self.kayit['oyun_sayisi']}\n"
                      f"En yüksek tasarruf: {tl(self.kayit['en_cok_tasarruf'])}")
        ctk.CTkLabel(pencere, text=istatistik, justify="left", text_color="#9fb0c8").pack(
            padx=20, pady=(12, 10), anchor="w")
        pencere.after(150, pencere.focus)


if __name__ == "__main__":
    PazarlikOyunu().mainloop()