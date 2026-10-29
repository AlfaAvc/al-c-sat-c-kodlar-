import tkinter as tk
import json
import random
import os

KAYIT_DOSYASI = "kayit.json"

# =====================================================================
# 1. OYUN VERİLERİ VE AYARLAR (Kod bilmeden kolayca düzenlenebilir alan)
# =====================================================================
OYUN_AYARLARI = {
    "magaza_adi": "TEKNO PAZAR - İKİNCİ EL & PROTOTİP MERKEZİ",
    "zorluklar": {
        "Kolay": {"sabir": 4, "butce_carpani": 1.25, "puan_carpani": 1.0},
        "Normal": {"sabir": 3, "butce_carpani": 1.05, "puan_carpani": 1.5},
        "Zor": {"sabir": 2, "butce_carpani": 0.90, "puan_carpani": 2.2}
    },
    "saticilar": [
        {
            "ad": "İnatçı Kazım Usta",
            "unvan": "Eski Esnaf",
            "emoji": "😠",
            "tema_rengi": "#ef4444",
            "karsilama": "Selamünaleyküm. Bakacaksan bak, vaktim dar. Mal ortada, ölücülük yapacaksan hiç başlama!",
            "inad_orani": 0.8 # İndirime direnç oranı
        },
        {
            "ad": "Tatlı Dilli Ayşe",
            "unvan": "Satış Danışmanı",
            "emoji": "😊",
            "tema_rengi": "#10b981",
            "karsilama": "Hoş geldin! Bugün şanslı günündesin, vitrindeki en temiz cihazı senin için çıkardım.",
            "inad_orani": 1.1
        },
        {
            "ad": "Donanım Kurdu Mert",
            "unvan": "Gömülü Sistem Uzmanı",
            "emoji": "🤓",
            "tema_rengi": "#6366f1",
            "karsilama": "Selam dostum! Elimde harika bir donanım var, anakartı ve devreleri bizzat kontrol ettim.",
            "inad_orani": 0.95
        },
        {
            "ad": "Kurnaz Cengiz",
            "unvan": "Komisyoncu",
            "emoji": "😏",
            "tema_rengi": "#f59e0b",
            "karsilama": "Kardeşim yabancı değilsin, geliş fiyatına bırakacağım sana. Kutusunu açmadan sarayım mı?",
            "inad_orani": 1.0
        }
    ],
    "urunler": [
        {"ad": "G-Phone 15 Pro", "ikon": "📱", "fiyat": 14000, "dip_fiyat": 11000, "aciklama": "256 GB, Kozmetik 9/10"},
        {"ad": "Samny Fold Z", "ikon": "📲", "fiyat": 18000, "dip_fiyat": 14500, "aciklama": "Katlanabilir Ekran, Kutulu"},
        {"ad": "Akıllı Gözlük Prototipi", "ikon": "🥽", "fiyat": 6500, "dip_fiyat": 4500, "aciklama": "Orange Pi Modüllü, HUD Ekranlı"},
        {"ad": "Retro Oyun Konsolu", "ikon": "🕹️", "fiyat": 4800, "dip_fiyat": 3400, "aciklama": "Özel Kasa, Çift Kollu"},
        {"ad": "Ultrabook X1 Carbon", "ikon": "💻", "fiyat": 22000, "dip_fiyat": 17500, "aciklama": "i7 İşlemci, 16 GB RAM"}
    ],
    "kusurlar": [
        {"metin": "Batarya sağlığı %55'e düşmüş, aniden kapanıyor!", "ciddiyet": 2200},
        {"metin": "Ekranın alt kısmında ölü pikseller ve hayalet ekran var!", "ciddiyet": 2800},
        {"metin": "Cihazda unutulmuş kilitli kullanıcı hesabı (Bypass gerekli)!", "ciddiyet": 3200},
        {"metin": "Şarj soketi temassızlık yapıyor, lehim tazelemek lazım.", "ciddiyet": 1500},
        None, # Kusursuz
        None
    ],
    "sonlar": {
        "son_1": {"baslik": "👑 Efsane Pazarlıkçı", "aciklama": "Tertemiz cihazı dip fiyata yakın kapatıp büyük kâr ettin!"},
        "son_2": {"baslik": "🤝 Makul Anlaşma", "aciklama": "Kusursuz cihazı ufak bir indirimle, değerinde satın aldın."},
        "son_3": {"baslik": "💸 Ağır Kazıklandın", "aciklama": "Pazarlık bile yapmadan satıcının ilk söylediği yüksek fiyattan aldın!"},
        "son_4": {"baslik": "💥 Kör Alışveriş (Ayıplı Mal)", "aciklama": "Cihazı incelemeden aldın! Eve gidince gizli kusuru fark ettin."},
        "son_5": {"baslik": "🛠️ Tamirci Ruhu (Uyanık Alıcı)", "aciklama": "Gizli kusuru buldun, fiyatı dibin de altına çekip tamir etmek için ucuza kapattın!"},
        "son_6": {"baslik": "🤬 Dükkandan Kovuldun!", "aciklama": "Satıcının sabrını sıfırladın, tezgahı kapatıp seni dışarı çıkardı."},
        "son_7": {"baslik": "🪙 Bütçe Yetmedi", "aciklama": "Fiyatı cüzdanındaki paraya kadar indiremedin ve eli boş döndün."},
        "son_8": {"baslik": "🕵️ Profesyonel Vazgeçiş", "aciklama": "Cihazdaki kusuru tespit ettin, riske girmeyip masadan kalktın."}
    }
}

# =====================================================================
# 2. ÖZEL MODERN BUTON SINIFI (Fare Üzerine Gelince Renk Değiştirir)
# =====================================================================
class HoverButton(tk.Button):
    def __init__(self, master, normal_bg, hover_bg, normal_fg="#ffffff", **kwargs):
        # Dışarıdan verilmediyse varsayılanları kullan (çakışmayı önler)
        kwargs.setdefault("padx", 12)
        kwargs.setdefault("pady", 8)
        kwargs.setdefault("font", ("Segoe UI", 10, "bold"))

        super().__init__(
            master,
            bg=normal_bg,
            fg=normal_fg,
            activebackground=hover_bg,
            activeforeground=normal_fg,
            relief="flat",
            bd=0,
            cursor="hand2",
            **kwargs
        )
        self.normal_bg = normal_bg
        self.hover_bg = hover_bg
        self.disabled_bg = "#334155"

        # Fare (Mouse) Etkileşimleri
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        if self["state"] != tk.DISABLED:
            self.config(bg=self.hover_bg)

    def on_leave(self, event):
        if self["state"] != tk.DISABLED:
            self.config(bg=self.normal_bg)

    def set_state(self, state):
        self.config(state=state)
        if state == tk.DISABLED:
            self.config(bg=self.disabled_bg, fg="#64748b", cursor="arrow")
        else:
            self.config(bg=self.normal_bg, fg="#ffffff", cursor="hand2")


# =====================================================================
# 3. ANA OYUN SINIFI
# =====================================================================
class PazarlikOyunu:
    def __init__(self, root):
        self.root = root
        self.root.title("Pazarlık Zamanı - Dönem Projesi Sürümü")
        self.root.geometry("820x680")
        self.root.configure(bg="#0f172a") # Koyu Lacivert/Arduvaz Arka Plan
        self.root.resizable(False, False)

        self.secili_zorluk = tk.StringVar(value="Normal")
        self.ses_acik = True
        self.daktilo_id = None

        self.kayitlari_yukle()
        self.arayuz_olustur()
        self.yeni_oyun()

    # --- KAYIT SİSTEMİ ---
    def kayitlari_yukle(self):
        if os.path.exists(KAYIT_DOSYASI):
            try:
                with open(KAYIT_DOSYASI, "r", encoding="utf-8") as f:
                    self.kayitlar = json.load(f)
            except Exception:
                self.kayitlar = {"kesfedilen_sonlar": [], "en_yuksek_puan": 0, "oynanan_oyun": 0}
        else:
            self.kayitlar = {"kesfedilen_sonlar": [], "en_yuksek_puan": 0, "oynanan_oyun": 0}

    def kaydet(self):
        with open(KAYIT_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(self.kayitlar, f, ensure_ascii=False, indent=4)

    def ses_cal(self):
        if self.ses_acik:
            self.root.bell()

    # --- ARAYÜZ TASARIMI ---
    def arayuz_olustur(self):
        # 1. ÜST BİLGİ ÇUBUĞU (HUD)
        self.ust_bar = tk.Frame(self.root, bg="#1e293b", height=60, pady=10, padx=15)
        self.ust_bar.pack(fill="x")

        tk.Label(
            self.ust_bar, text=f"🏪 {OYUN_AYARLARI['magaza_adi']}",
            font=("Segoe UI", 12, "bold"), bg="#1e293b", fg="#38bdf8"
        ).pack(side="left")

        # Sağ Üst Kontroller
        self.btn_sonlar = HoverButton(
            self.ust_bar, normal_bg="#eab308", hover_bg="#facc15", normal_fg="#0f172a",
            text="🏆 Sonlarım (0/8)", command=self.sonlari_goster, pady=4, padx=10
        )
        self.btn_sonlar.pack(side="right", padx=5)

        self.btn_ses = HoverButton(
            self.ust_bar, normal_bg="#334155", hover_bg="#475569",
            text="🔊 Ses", command=self.ses_degistir, pady=4, padx=8
        )
        self.btn_ses.pack(side="right", padx=5)

        # Zorluk Seçici
        zorluk_frame = tk.Frame(self.ust_bar, bg="#1e293b")
        zorluk_frame.pack(side="right", padx=10)
        tk.Label(zorluk_frame, text="Zorluk:", bg="#1e293b", fg="#94a3b8", font=("Segoe UI", 9, "bold")).pack(side="left", padx=3)
        for z in ["Kolay", "Normal", "Zor"]:
            rb = tk.Radiobutton(
                zorluk_frame, text=z, variable=self.secili_zorluk, value=z,
                command=self.yeni_oyun, bg="#1e293b", fg="#f8fafc", selectcolor="#0f172a",
                activebackground="#1e293b", activeforeground="#38bdf8", font=("Segoe UI", 9)
            )
            rb.pack(side="left")

        # 2. İSTATİSTİK ŞERİDİ (Cüzdan, Fiyat, Rekor)
        self.stat_bar = tk.Frame(self.root, bg="#0f172a", pady=8, padx=15)
        self.stat_bar.pack(fill="x")

        self.lbl_cuzdan = tk.Label(self.stat_bar, text="💳 Cüzdan: 0 TL", font=("Segoe UI", 11, "bold"), bg="#1e293b", fg="#4ade80", padx=12, pady=6)
        self.lbl_cuzdan.pack(side="left", padx=(0, 10))

        self.lbl_fiyat = tk.Label(self.stat_bar, text="🏷️ İstenen Fiyat: 0 TL", font=("Segoe UI", 11, "bold"), bg="#1e293b", fg="#fbbf24", padx=12, pady=6)
        self.lbl_fiyat.pack(side="left", padx=10)

        self.lbl_durum_etiketi = tk.Label(self.stat_bar, text="🔎 Durum: İncelenmedi", font=("Segoe UI", 10, "bold"), bg="#1e293b", fg="#94a3b8", padx=12, pady=6)
        self.lbl_durum_etiketi.pack(side="left", padx=10)

        self.lbl_rekor = tk.Label(self.stat_bar, text=f"⭐ En Yüksek Puan: {self.kayitlar['en_yuksek_puan']}", font=("Segoe UI", 10, "bold"), bg="#1e293b", fg="#c084fc", padx=12, pady=6)
        self.lbl_rekor.pack(side="right")

        # 3. GÖRSEL SAHNE ALANI (Canvas ile Çizilen Dükkan)
        self.sahne = tk.Canvas(self.root, width=790, height=230, bg="#1e293b", highlightthickness=2, highlightbackground="#334155")
        self.sahne.pack(padx=15, pady=5)

        # 4. DİYALOG KUTUSU
        self.diyalog_frame = tk.Frame(self.root, bg="#1e293b", highlightbackground="#38bdf8", highlightthickness=1, padx=15, pady=12)
        self.diyalog_frame.pack(fill="x", padx=15, pady=8)

        self.lbl_konusan = tk.Label(self.diyalog_frame, text="Satıcı", font=("Segoe UI", 11, "bold"), bg="#1e293b", fg="#38bdf8", anchor="w")
        self.lbl_konusan.pack(fill="x")

        self.lbl_diyalog = tk.Label(
            self.diyalog_frame, text="", font=("Segoe UI", 11),
            bg="#1e293b", fg="#f8fafc", wraplength=750, justify="left", anchor="w", height=3
        )
        self.lbl_diyalog.pack(fill="x", pady=(4, 0))

        # 5. SEÇENEKLER VE AKSİYON BUTONLARI (Mouse Hover Destekli)
        self.aksiyon_frame = tk.Frame(self.root, bg="#0f172a", padx=15, pady=5)
        self.aksiyon_frame.pack(fill="both", expand=True)

        tk.Label(
            self.aksiyon_frame, text="⚡ Hamleni Seç (Seçeneklerin üzerine gelerek detayları görebilirsin):",
            font=("Segoe UI", 10, "bold"), bg="#0f172a", fg="#94a3b8", anchor="w"
        ).pack(fill="x", pady=(0, 6))

        btn_grid = tk.Frame(self.aksiyon_frame, bg="#0f172a")
        btn_grid.pack(fill="x")
        btn_grid.columnconfigure(0, weight=1)
        btn_grid.columnconfigure(1, weight=1)

        self.btn_incele = HoverButton(
            btn_grid, normal_bg="#0284c7", hover_bg="#38bdf8",
            text="🔍 1. Cihazı Detaylı İncele (Gizli kusur kontrolü)", command=self.incele
        )
        self.btn_incele.grid(row=0, column=0, columnspan=2, sticky="ew", padx=4, pady=4)

        self.btn_nazik_pazarlik = HoverButton(
            btn_grid, normal_bg="#4f46e5", hover_bg="#818cf8",
            text="💬 2. Nazikçe İndirim İste (Düşük Risk - 1 Sabır)", command=lambda: self.pazarlik_yap("nazik")
        )
        self.btn_nazik_pazarlik.grid(row=1, column=0, sticky="ew", padx=4, pady=4)

        self.btn_sert_pazarlik = HoverButton(
            btn_grid, normal_bg="#d97706", hover_bg="#fbbf24",
            text="🔥 3. Kusuru/Piyasayı Öne Sür (Yüksek İndirim - Yüksek Risk)", command=lambda: self.pazarlik_yap("sert")
        )
        self.btn_sert_pazarlik.grid(row=1, column=1, sticky="ew", padx=4, pady=4)

        self.btn_satin_al = HoverButton(
            btn_grid, normal_bg="#059669", hover_bg="#34d399",
            text="🤝 4. Anlaş ve Satın Al", command=self.satin_al
        )
        self.btn_satin_al.grid(row=2, column=0, sticky="ew", padx=4, pady=4)

        self.btn_ayril = HoverButton(
            btn_grid, normal_bg="#e11d48", hover_bg="#fb7185",
            text="🚶 5. Masadan Kalk / Yeni Dükkana Git", command=self.ayril
        )
        self.btn_ayril.grid(row=2, column=1, sticky="ew", padx=4, pady=4)

        self.son_butonunu_guncelle()

    # --- SAHNE ÇİZİM MOTORU (CANVAS) ---
    def sahneyi_ciz(self, sahne_rengi="#1e293b", yuz_emojisi=None, durum_mesaji="PAZARLIK SÜRÜYOR"):
        self.sahne.delete("all")
        self.sahne.config(bg=sahne_rengi)

        # Arka plan dükkan rafları ve tente
        self.sahne.create_rectangle(0, 0, 790, 35, fill="#0f172a", outline="")
        for i in range(0, 800, 40):
            renk = "#e11d48" if (i // 40) % 2 == 0 else "#f8fafc"
            self.sahne.create_rectangle(i, 0, i + 40, 12, fill=renk, outline="")

        # Tezgah
        self.sahne.create_rectangle(0, 175, 790, 230, fill="#334155", outline="#475569", width=2)
        self.sahne.create_line(0, 175, 790, 175, fill="#94a3b8", width=2)

        # Sol Taraf: Satıcı Avatarı ve Sabır Çubuğu
        s_renk = self.satici["tema_rengi"]
        emoji = yuz_emojisi if yuz_emojisi else self.satici["emoji"]

        self.sahne.create_oval(45, 45, 145, 145, fill="#0f172a", outline=s_renk, width=4)
        self.sahne.create_text(95, 95, text=emoji, font=("Segoe UI Emoji", 42))
        self.sahne.create_text(95, 160, text=self.satici["ad"], font=("Segoe UI", 10, "bold"), fill="#f8fafc")

        # Satıcı Sabır Barı
        self.sahne.create_text(250, 55, text="SATICI SABRI & GÜVENİ", font=("Segoe UI", 9, "bold"), fill="#94a3b8", anchor="w")
        self.sahne.create_rectangle(250, 70, 450, 92, fill="#0f172a", outline="#475569", width=2)

        oran = max(0, self.sabir / self.max_sabir)
        bar_renk = "#22c55e" if oran > 0.6 else ("#eab308" if oran > 0.3 else "#ef4444")
        if oran > 0:
            self.sahne.create_rectangle(252, 72, 252 + int(196 * oran), 90, fill=bar_renk, outline="")
        self.sahne.create_text(350, 81, text=f"{self.sabir} / {self.max_sabir} Hak", font=("Segoe UI", 9, "bold"), fill="#ffffff")

        # Sahne Durum Rozeti
        self.sahne.create_rectangle(250, 110, 450, 145, fill="#0f172a", outline=s_renk, width=1)
        self.sahne.create_text(350, 127, text=durum_mesaji, font=("Segoe UI", 10, "bold"), fill="#38bdf8")

        # Sağ Taraf: Tezgahtaki Cihaz Kutusu
        self.sahne.create_rectangle(500, 40, 760, 165, fill="#0f172a", outline="#38bdf8", width=2)
        self.sahne.create_text(555, 102, text=self.urun["ikon"], font=("Segoe UI Emoji", 40))
        self.sahne.create_text(600, 70, text=self.urun["ad"], font=("Segoe UI", 11, "bold"), fill="#f8fafc", anchor="w", width=150)
        self.sahne.create_text(600, 105, text=self.urun["aciklama"], font=("Segoe UI", 9), fill="#94a3b8", anchor="w", width=150)
        self.sahne.create_text(600, 140, text=f"Etiket: {self.mevcut_fiyat} TL", font=("Segoe UI", 11, "bold"), fill="#fbbf24", anchor="w")

    # --- DAKTİLO EFEKTLİ METİN YAZDIRMA ---
    def diyalog_yaz(self, konusan, metin, renk="#38bdf8"):
        if self.daktilo_id:
            self.root.after_cancel(self.daktilo_id)
        self.lbl_konusan.config(text=konusan, fg=renk)
        self.lbl_diyalog.config(text="")
        self._harf_ekle(metin, 0)

    def _harf_ekle(self, metin, indeks):
        if indeks <= len(metin):
            self.lbl_diyalog.config(text=metin[:indeks])
            self.daktilo_id = self.root.after(14, self._harf_ekle, metin, indeks + 1)

    # --- OYUN AKIŞI VE MEKANİKLER ---
    def yeni_oyun(self):
        zorluk_bilgi = OYUN_AYARLARI["zorluklar"][self.secili_zorluk.get()]
        self.satici = random.choice(OYUN_AYARLARI["saticilar"])
        self.urun = random.choice(OYUN_AYARLARI["urunler"])
        self.kusur = random.choice(OYUN_AYARLARI["kusurlar"])

        self.ilk_fiyat = self.urun["fiyat"]
        self.mevcut_fiyat = self.urun["fiyat"]
        self.dip_fiyat = self.urun["dip_fiyat"]

        # Kusurlu cihazda gerçek dip fiyat daha düşüktür
        if self.kusur:
            self.gercek_dip = max(1500, self.dip_fiyat - self.kusur["ciddiyet"])
        else:
            self.gercek_dip = self.dip_fiyat

        self.max_sabir = zorluk_bilgi["sabir"]
        self.sabir = self.max_sabir
        self.butce = int(self.dip_fiyat * zorluk_bilgi["butce_carpani"] + random.randint(200, 1200))

        self.incelendi = False
        self.pazarlik_sayisi = 0

        self.etiketleri_guncelle()
        self.lbl_durum_etiketi.config(text="🔎 Durum: İncelenmedi", fg="#94a3b8")
        self.sahneyi_ciz(sahne_rengi="#1e293b", durum_mesaji="MAĞAZAYA GİRİLDİ")
        self.diyalog_yaz(
            f"{self.satici['ad']} ({self.satici['unvan']})",
            f"\"{self.satici['karsilama']}\"",
            self.satici["tema_rengi"]
        )

        for btn in [self.btn_incele, self.btn_nazik_pazarlik, self.btn_sert_pazarlik, self.btn_satin_al]:
            btn.set_state(tk.NORMAL)
        self.btn_ayril.config(text="🚶 5. Masadan Kalk (Vazgeç)")

    def etiketleri_guncelle(self):
        self.lbl_cuzdan.config(text=f"💳 Cüzdan: {self.butce} TL")
        renk = "#4ade80" if self.mevcut_fiyat <= self.butce else "#f87171"
        self.lbl_fiyat.config(text=f"🏷️ Güncel Fiyat: {self.mevcut_fiyat} TL", fg=renk)
        self.lbl_rekor.config(text=f"⭐ En Yüksek Puan: {self.kayitlar['en_yuksek_puan']}")

    def son_butonunu_guncelle(self):
        toplam = len(OYUN_AYARLARI["sonlar"])
        bulunan = len(self.kayitlar["kesfedilen_sonlar"])
        self.btn_sonlar.config(text=f"🏆 Sonlarım ({bulunan}/{toplam})")

    def ses_degistir(self):
        self.ses_acik = not self.ses_acik
        self.btn_ses.config(text="🔊 Ses" if self.ses_acik else "🔇 Sessiz")

    # --- AKSİYON 1: İNCELEME ---
    def incele(self):
        self.incelendi = True
        self.btn_incele.set_state(tk.DISABLED)
        self.ses_cal()

        if self.kusur:
            self.lbl_durum_etiketi.config(text="⚠️ KUSUR TESPİT EDİLDİ!", fg="#f87171")
            self.sahneyi_ciz(sahne_rengi="#3b1d2e", yuz_emojisi="😰", durum_mesaji="KUSUR YAKALANDI!")
            self.diyalog_yaz(
                "🔍 Teknik İnceleme Raporu",
                f"DİKKAT! Cihazı test ederken gizli bir sorun buldun: {self.kusur['metin']} "
                f"Şimdi 'Kusuru Öne Sür' butonuyla fiyatı çok sert kırabilirsin!",
                "#f87171"
            )
        else:
            self.lbl_durum_etiketi.config(text="✅ Cihaz Kusursuz", fg="#4ade80")
            self.sahneyi_ciz(sahne_rengi="#132a2e", yuz_emojisi="😎", durum_mesaji="CİHAZ SAPASAĞLAM")
            self.diyalog_yaz(
                "🔍 Teknik İnceleme Raporu",
                "Tüm donanım ve ekran testlerini yaptın. Cihazda hiçbir gizli kusur yok, gönül rahatlığıyla pazarlık yapabilirsin.",
                "#4ade80"
            )

    # --- AKSİYON 2 & 3: PAZARLIK ---
    def pazarlik_yap(self, tur):
        self.pazarlik_sayisi += 1
        inad = self.satici["inad_orani"]

        if tur == "nazik":
            self.sabir -= 1
            temel_indirim = int(random.randint(450, 950) * inad)
            if self.incelendi and self.kusur:
                temel_indirim += 500
            teklif_metni = "Hocam öğrenciyim, bütçem kısıtlı. Bize bir güzellik yapmaz mısın?"
        else:
            # Sert pazarlık: Kusur bulunduysa çok etkili, bulunmadıysa satıcıyı kızdırır
            if self.incelendi and self.kusur:
                self.sabir -= 1
                temel_indirim = int(random.randint(1400, 2400) * inad)
                teklif_metni = f"Usta bu cihaz arızalı! ({self.kusur['metin']}) Bu fiyata imkanı yok almam, gerçek değerine in!"
            else:
                self.sabir -= 2 # Kanıtsız sert pazarlık sabrı 2 kat tüketir!
                temel_indirim = int(random.randint(700, 1400) * inad)
                teklif_metni = "Piyasada bunun yarı fiyatına satıyorlar, çok uçmuşsun! İndir fiyatı alayım."

        if self.sabir <= 0:
            self.sabir = 0
            self.oyunu_bitir("son_6") # Kovuldun
            return

        yeni_fiyat = max(self.gercek_dip, self.mevcut_fiyat - temel_indirim)

        if yeni_fiyat < self.mevcut_fiyat:
            yapilan_indirim = self.mevcut_fiyat - yeni_fiyat
            self.mevcut_fiyat = yeni_fiyat
            self.etiketleri_guncelle()
            self.sahneyi_ciz(sahne_rengi="#1e1b4b", yuz_emojisi="🤔", durum_mesaji=f"-{yapilan_indirim} TL İNDİRİM!")
            self.diyalog_yaz(
                f"Sen ➔ {self.satici['ad']}",
                f"Sen: \"{teklif_metni}\"\n"
                f"{self.satici['ad']}: \"Elimi kolumu bağladın... Hadi {yapilan_indirim} TL daha düştüm, {self.mevcut_fiyat} TL olsun!\"",
                "#fbbf24"
            )
        else:
            self.etiketleri_guncelle()
            self.sahneyi_ciz(sahne_rengi="#3f1d24", yuz_emojisi="😤", durum_mesaji="DİP FİYATA ULAŞILDI")
            self.diyalog_yaz(
                self.satici["ad"],
                f"\"Kusura bakma, {self.mevcut_fiyat} TL'den tek kuruş aşağı inmem! Zorlarsan satmaktan vazgeçeceğim.\"",
                "#f87171"
            )

    # --- AKSİYON 4: SATIN AL ---
    def satin_al(self):
        if self.mevcut_fiyat > self.butce:
            self.oyunu_bitir("son_7") # Bütçe yetmedi
            return

        if not self.incelendi and self.kusur:
            self.oyunu_bitir("son_4") # Kör alışveriş
        elif self.incelendi and self.kusur:
            self.oyunu_bitir("son_5") # Uyanık alıcı (Tamirci)
        elif self.pazarlik_sayisi == 0:
            self.oyunu_bitir("son_3") # Pazarlıksız kazıklandı
        elif self.mevcut_fiyat <= self.dip_fiyat + 400:
            self.oyunu_bitir("son_1") # Efsane pazarlıkçı
        else:
            self.oyunu_bitir("son_2") # Makul anlaşma

    # --- AKSİYON 5: AYRIL / YENİ OYUN ---
    def ayril(self):
        if self.btn_satin_al["state"] == tk.DISABLED:
            self.yeni_oyun()
        else:
            self.oyunu_bitir("son_8")

    # --- OYUN SONU VE PUAN HESAPLAMA ---
    def oyunu_bitir(self, son_id):
        self.ses_cal()
        for btn in [self.btn_incele, self.btn_nazik_pazarlik, self.btn_sert_pazarlik, self.btn_satin_al]:
            btn.set_state(tk.DISABLED)
        self.btn_ayril.config(text="🔄 Yeni Müşteri Olarak Tekrar Oyna")

        son_bilgi = OYUN_AYARLARI["sonlar"][son_id]
        zorluk_carpani = OYUN_AYARLARI["zorluklar"][self.secili_zorluk.get()]["puan_carpani"]

        # Puan Hesabı
        indirim_kari = self.ilk_fiyat - self.mevcut_fiyat
        if son_id in ["son_1", "son_5"]:
            puan = int((1200 + indirim_kari) * zorluk_carpani)
            sahne_renk, emoji = "#064e3b", "🥳"
        elif son_id in ["son_2", "son_8"]:
            puan = int((600 + indirim_kari * 0.5) * zorluk_carpani)
            sahne_renk, emoji = "#1e3a8a", "🤝"
        else:
            puan = 100
            sahne_renk, emoji = "#450a0a", "💀"

        # Kayıt Güncelleme
        self.kayitlar["oynanan_oyun"] = self.kayitlar.get("oynanan_oyun", 0) + 1
        yeni_son_acildi = False
        if son_id not in self.kayitlar["kesfedilen_sonlar"]:
            self.kayitlar["kesfedilen_sonlar"].append(son_id)
            yeni_son_acildi = True

        if puan > self.kayitlar.get("en_yuksek_puan", 0):
            self.kayitlar["en_yuksek_puan"] = puan

        self.kaydet()
        self.etiketleri_guncelle()
        self.son_butonunu_guncelle()

        ek_bilgi = " (🎉 YENİ SON KEŞFEDİLDİ!)" if yeni_son_acildi else ""
        self.sahneyi_ciz(sahne_rengi=sahne_renk, yuz_emojisi=emoji, durum_mesaji=f"PUAN: {puan}")
        self.diyalog_yaz(
            f"OYUN BİTTİ: {son_bilgi['baslik']}{ek_bilgi}",
            f"{son_bilgi['aciklama']} | Kazanılan Puan: {puan} (Toplam {len( OYUN_AYARLARI['sonlar'] )} sondan {len(self.kayitlar['kesfedilen_sonlar'])} tanesine ulaştın.)",
            "#facc15"
        )

    # --- ÖZEL TASARIM "SONLARIM" PENCERESİ (MODAL) ---
    def sonlari_goster(self):
        pencere = tk.Toplevel(self.root)
        pencere.title("Sonlarım ve Başarımlar")
        pencere.geometry("560x520")
        pencere.configure(bg="#0f172a")
        pencere.resizable(False, False)

        bulunan = len(self.kayitlar["kesfedilen_sonlar"])
        toplam = len(OYUN_AYARLARI["sonlar"])

        tk.Label(
            pencere, text=f"🏆 KEŞFEDİLEN SONLAR ({bulunan} / {toplam})",
            font=("Segoe UI", 14, "bold"), bg="#0f172a", fg="#facc15", pady=10
        ).pack()

        tk.Label(
            pencere,
            text=f"En Yüksek Puan: {self.kayitlar.get('en_yuksek_puan', 0)}   |   Toplam Oynanan Oyun: {self.kayitlar.get('oynanan_oyun', 0)}",
            font=("Segoe UI", 10, "bold"), bg="#1e293b", fg="#38bdf8", padx=15, pady=6
        ).pack(fill="x", padx=20, pady=(0, 10))

        liste_frame = tk.Frame(pencere, bg="#0f172a")
        liste_frame.pack(fill="both", expand=True, padx=20)

        for s_id, s_bilgi in OYUN_AYARLARI["sonlar"].items():
            acik_mi = s_id in self.kayitlar["kesfedilen_sonlar"]
            kart_bg = "#1e293b" if acik_mi else "#090d16"
            kenar_renk = "#22c55e" if acik_mi else "#334155"

            kart = tk.Frame(liste_frame, bg=kart_bg, highlightbackground=kenar_renk, highlightthickness=1, padx=10, pady=6)
            kart.pack(fill="x", pady=3)

            if acik_mi:
                tk.Label(kart, text=s_bilgi["baslik"], font=("Segoe UI", 10, "bold"), bg=kart_bg, fg="#4ade80", anchor="w").pack(fill="x")
                tk.Label(kart, text=s_bilgi["aciklama"], font=("Segoe UI", 9), bg=kart_bg, fg="#cbd5e1", anchor="w").pack(fill="x")
            else:
                tk.Label(kart, text="🔒 ??? (Kilitli Son)", font=("Segoe UI", 10, "bold"), bg=kart_bg, fg="#64748b", anchor="w").pack(fill="x")
                tk.Label(kart, text="Bu sona ulaşmak için farklı bir pazarlık stratejisi dene.", font=("Segoe UI", 9, "italic"), bg=kart_bg, fg="#475569", anchor="w").pack(fill="x")

        HoverButton(
            pencere, normal_bg="#e11d48", hover_bg="#fb7185",
            text="Kapat", command=pencere.destroy
        ).pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = PazarlikOyunu(root)
    root.mainloop()