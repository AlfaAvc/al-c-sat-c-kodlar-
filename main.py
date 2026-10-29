"""PAZARLIK ZAMANI v2.0 — İkinci El Teknoloji Pazarı
Kurulum : py -m pip install customtkinter
Çalıştır: py main.py

Özellikler:
1. Değişen Sahne Görselleri & Canlı Satıcı Yüz İfadeleri (Emoji/Renk + images/*.png desteği)
2. Kalıcı Son Geçmişi ve En Yüksek Puan (kayit.json) + "Sonlarım" Koleksiyon Penceresi
3. Tek Merkezden Özelleştirilebilir Oyun Ayarları (OYUN_AYARLARI sözlüğü)
4. Gizli Kusur Stratejisi (Pil, Ekran, Kilitli Hesap, Kamera)
5. Farklı Telefonlar/Cihazlar ve Farklı Satıcı Karakterleri
6. Sınırlı Pazarlık Hakkı (Sabır Sistemi) ve Selamlaşma Aşaması
7. 8 Farklı Oyun Sonu, Zorluk Seviyeleri (Kolay/Normal/Zor) ve Ses Efektleri
"""

import json
import os
import random
import threading
import tkinter as tk
import customtkinter as ctk

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

KAYIT_DOSYASI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kayit.json")
GORSEL_KLASORU = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")

# ============================================================================
# 3. KENDİ FİKİRLERİN (OYUN AYARLARI)
# Kod bilmeden aşağıdaki metinleri, satıcıları, ürünleri ve fiyatları
# dilediğin gibi değiştirebilir veya yenilerini ekleyebilirsin!
# ============================================================================
OYUN_AYARLARI = {
    "magaza_adi": "📱 PAZARLIK ZAMANI",
    "magaza_alt_baslik": "İkinci El Teknoloji Pazarı · İncele, nabız yokla, pazarlık yap ve en iyi anlaşmayı yakala!",

    "zorluklar": {
        "Kolay": {
            "butce_carpani": 1.15,
            "ek_sabir": 1,
            "kusur_ihtimali": 0.30,
            "puan_carpani": 0.90,
            "aciklama": "Yüksek bütçe, sabırlı satıcılar, düşük gizli kusur riski."
        },
        "Normal": {
            "butce_carpani": 1.00,
            "ek_sabir": 0,
            "kusur_ihtimali": 0.55,
            "puan_carpani": 1.00,
            "aciklama": "Dengeli bütçe, standart pazarlık hakkı ve normal kusur riski."
        },
        "Zor": {
            "butce_carpani": 0.92,
            "ek_sabir": -1,
            "kusur_ihtimali": 0.75,
            "puan_carpani": 1.25,
            "aciklama": "Kısıtlı bütçe (pazarlık şart!), çetin satıcılar, yüksek kusur riski."
        },
    },

    "saticilar": [
        {
            "ad": "Hasan Abi",
            "unvan": "Kalender Esnaf",
            "karakter": "Cana yakın, geleneksel esnaf. Güler yüzlü ve saygılı müşteriyi sever.",
            "baz_sabir": 4,
            "esneklik": 1.15,
            "karsilama": "Tezgahın arkasında çayını yudumluyor. Seni görünce hafifçe doğruldu.",
            "selam_cevap": {
                "saygili": "Aleykümselam güzel kardeşim, hoş geldin! Çay söyleyeyim mi? Buyur, hangi cihaza bakmıştın?",
                "normal": "Hoş geldiniz, iyi günler. Buyurun, vitrindeki cihazlara birlikte bakalım.",
                "kaba": "Hayırdır delikanlı, bir selam verseydin önce... Neyse, fiyat etikette yazıyor, çok bir şey inmem."
            }
        },
        {
            "ad": "İnatçı Kazım",
            "unvan": "Sert Pazarlıkçı",
            "karakter": "Sinirli ve sabırsız. Ölücü tekliflere ve kabalığa hiç gelemez.",
            "baz_sabir": 3,
            "esneklik": 0.85,
            "karsilama": "Kollarını bağlamış vitrini izliyor. Ciddi bir ifadeyle sana döndü.",
            "selam_cevap": {
                "saygili": "Aleykümselam, sağ olasın. Ciddi alıcıysan buyur konuşalım, elimdeki mal temizdir.",
                "normal": "Merhaba. Alıcıysan cihaz burada, vaktim kısıtlı ona göre konuşalım.",
                "kaba": "Hop yavaş gel! Selam yok sabah yok direkt son fiyat soruyorsun. İşine gelirse fiyat orada!"
            }
        },
        {
            "ad": "Tatlı Dilli Ayşe",
            "unvan": "Kurnaz Satıcı",
            "karakter": "Çok güler yüzlü ve ikna edici ama cihazı pahalıya satmaya çalışır.",
            "baz_sabir": 3,
            "esneklik": 0.95,
            "karsilama": "Yüzünde kocaman bir gülümsemeyle tezgahı siliyor.",
            "selam_cevap": {
                "saygili": "Hoş geldiniz, ne kadar kibarsınız! Size bugün dükkanın en gözde cihazını vereceğim!",
                "normal": "Hoş geldin! Tam sana göre pırıl pırıl bir cihazım var, kaçırsan üzülürsün.",
                "kaba": "Ay aşk olsun, insan önce bir merhaba der! Bu fiyata böyle cihaz bulamazsın, söyleyeyim."
            }
        },
        {
            "ad": "Teknoloji Kurdu Mert",
            "unvan": "Donanım Uzmanı",
            "karakter": "Teknik detaylara hakim. Cihazı inceleyen bilinçli alıcıya saygı duyar.",
            "baz_sabir": 4,
            "esneklik": 1.05,
            "karsilama": "Elinde tornavida ve ölçü aletiyle anakart inceliyor.",
            "selam_cevap": {
                "saygili": "Selamlar dostum, hoş geldin! Donanımdan anlayan müşteri başımın tacıdır, buyur inceleyelim.",
                "normal": "Merhaba! Elimde testlerini yaptığım güzel bir cihaz var, bakmak ister misin?",
                "kaba": "Dostum burası semt pazarı değil, önce cihazın donanımına bak sonra fiyat konuşuruz."
            }
        }
    ],

    "urunler": [
        {
            "ad": "iPhone 12 (128 GB)",
            "ikon": "📱",
            "fiyat": 8500,
            "dip_fiyat": 7300,
            "vitrin_bilgisi": "Durum: İyi · Görünür Pil: %84 · Kutu mevcut"
        },
        {
            "ad": "G-Phone X Pro (256 GB)",
            "ikon": "📲",
            "fiyat": 10000,
            "dip_fiyat": 8200,
            "vitrin_bilgisi": "Durum: Çok İyi · Görünür Pil: %88 · Şarj aleti dahil"
        },
        {
            "ad": "Samny Z Katlanabilir",
            "ikon": "📟",
            "fiyat": 15000,
            "dip_fiyat": 12600,
            "vitrin_bilgisi": "Durum: Özel Seri · Menteşesi sağlam · Kılıf hediyeli"
        },
        {
            "ad": "Akıllı Gözlük Prototipi (Orange Pi Modüllü)",
            "ikon": "🕶️",
            "fiyat": 4500,
            "dip_fiyat": 3200,
            "vitrin_bilgisi": "Durum: Geliştirici Sürümü · Kamera & Ekran modülü aktif"
        },
        {
            "ad": "Redmi Note 12 Pro",
            "ikon": "📱",
            "fiyat": 6800,
            "dip_fiyat": 5600,
            "vitrin_bilgisi": "Durum: Temiz · 67W Hızlı Şarj · Kutu ve fatura mevcut"
        }
    ],

    "kusurlar": [
        {
            "kod": "pil",
            "baslik": "Gizli Batarya Şişmesi & Ani Kapanma",
            "inceleme_metni": "Ayarlarda pil %84 görünse de batarya testinde voltaj çökmesi yakaladın! Cihaz yük altında aniden kapanıyor, batarya değişimi şart.",
            "pazarlik_kozu": "Ustam bu cihazın bataryası ömrünü tamamlamış, yük altında kapanıyor. Pil masrafını düşelim!",
            "ek_indirim_orani": 0.14
        },
        {
            "kod": "ekran",
            "baslik": "Ekranda Ölü Piksel & Hayalet Dokunuş",
            "inceleme_metni": "Ekran parlaklığını sona alıp beyaz test ekranı açtığında alt köşede ölü pikseller ve kendi kendine basma (ghost touch) sorunu fark ettin!",
            "pazarlik_kozu": "Ekranda ölü pikseller ve dokunmatik titremesi var, ekran masrafı çıkacak. Fiyatı ona göre kırarsan alırım.",
            "ek_indirim_orani": 0.16
        },
        {
            "kod": "kilit",
            "baslik": "Unutulmuş Kilitli Hesap (Bulut Kilidi)",
            "inceleme_metni": "Ayarların derinliklerine girdiğinde eski sahibinin bulut hesabının açık kaldığını ve sıfırlama kilidi olduğunu fark ettin!",
            "pazarlik_kozu": "Cihazda kilitli hesap kalmış, yazılım ve kilit açma masrafı var. Dip fiyattan verirsen yedek parça/çözüm için alayım.",
            "ek_indirim_orani": 0.18
        },
        {
            "kod": "kamera",
            "baslik": "Kamera Optik Odaklama (OIS) Arızası",
            "inceleme_metni": "Kamerayı 2x yakınlaştırmaya aldığında lens motorunun titrediğini ve görüntüyü netleyemediğini tespit ettin!",
            "pazarlik_kozu": "Kameranın odaklama motoru titriyor, net çekim yapmıyor. Kamera tamir payını düşersen anlaşalım.",
            "ek_indirim_orani": 0.13
        }
    ],

    "sahneler": {
        "giris": {
            "emoji": "🏪",
            "baslik": "Mağazaya Giriş",
            "alt_yazi": "Dükkana adım attın. İlk selamın pazarlığın havasını belirleyecek!",
            "renk": "#132338",
            "vurgu": "#38bdf8",
            "resim": "giris.png"
        },
        "vitrin": {
            "emoji": "📱✨",
            "baslik": "Tezgah Başında",
            "alt_yazi": "Cihaz tezgahta duruyor. İnceleyecek misin yoksa direkt fiyata mı gireceksin?",
            "renk": "#162a42",
            "vurgu": "#60a5fa",
            "resim": "vitrin.png"
        },
        "inceleme_temiz": {
            "emoji": "🔎✅",
            "baslik": "İnceleme Sonucu: KUSURSUZ CİHAZ",
            "alt_yazi": "Ekran, batarya, anakart ve hesap kontrolleri tertemiz çıktı!",
            "renk": "#113328",
            "vurgu": "#34d399",
            "resim": "inceleme_temiz.png"
        },
        "inceleme_kusurlu": {
            "emoji": "🧐⚠️",
            "baslik": "İnceleme Sonucu: GİZLİ KUSUR YAKALANDI!",
            "alt_yazi": "Dikkatli kontrolün sayesinde satıcının söylemediği bir kusur buldun!",
            "renk": "#3b2812",
            "vurgu": "#fbbf24",
            "resim": "inceleme_kusurlu.png"
        },
        "pazarlik": {
            "emoji": "🤝💬",
            "baslik": "Fiyat Pazarlığı",
            "alt_yazi": "Satıcının sabrını taşırmadan en uygun fiyatı koparmaya çalış!",
            "renk": "#231d3b",
            "vurgu": "#a78bfa",
            "resim": "pazarlik.png"
        }
    },

    "sonlar": {
        "son_1": {
            "baslik": "SON 1 — KUSURSUZ KAZANÇ (USTA ALICI)",
            "kisa_ad": "Kusursuz Kazanç (Usta Alıcı)",
            "emoji": "🏆",
            "renk": "#123829",
            "vurgu": "#34d399",
            "resim": "son_1.png",
            "metin": "Cihazı titizlikle inceledin, temiz olduğunu doğruladın, satıcının güvenini kazanarak harika bir indirimle bütçeni koruyup satın aldın!",
            "ipucu": "Kusursuz bir cihazı incele, satıcı güvenini yüksek tut ve iyi bir pazarlıkla bütçeni aşmadan al."
        },
        "son_2": {
            "baslik": "SON 2 — KAZIKLANDIN & BÜTÇE AŞIMI",
            "kisa_ad": "Kazıklandın & Bütçe Aşımı",
            "emoji": "💸",
            "renk": "#3d1a24",
            "vurgu": "#f87171",
            "resim": "son_2.png",
            "metin": "Bütçeni aşarak borca girdin veya cihaza değerinden çok yüksek bir para ödeyerek memnuniyetsiz ayrıldın.",
            "ipucu": "Bütçeni aşarak veya memnuniyetin çok düşükken pahalıya satın al."
        },
        "son_3": {
            "baslik": "SON 3 — KÖR ALIŞVERİŞ (GİZLİ KUSUR ŞOKU!)",
            "kisa_ad": "Kör Alışveriş (Gizli Kusur)",
            "emoji": "💥",
            "renk": "#451818",
            "vurgu": "#ef4444",
            "resim": "son_3.png",
            "metin": "Cihazı hiç incelemeden satın aldın! Eve gittiğinde gizli kusur ortaya çıktı ve elinde arızalı cihazla pişman oldun.",
            "ipucu": "Gizli kusuru olan bir cihazı hiç incelemeden satın al."
        },
        "son_4": {
            "baslik": "SON 4 — SABIR TAŞTI (DÜKKANDAN KOVULDUN!)",
            "kisa_ad": "Kovuldun! (Sabır Taştı)",
            "emoji": "🤬",
            "renk": "#471419",
            "vurgu": "#fb7185",
            "resim": "son_4.png",
            "metin": "Aşırı ısrarcı veya ölücü tekliflerle satıcının bütün sabrını tükettin! Satıcı telefonu tezgahtan kaldırıp seni dükkandan kovdu.",
            "ipucu": "Pazarlıkta satıcının sabır kalplerini sıfıra indir."
        },
        "son_5": {
            "baslik": "SON 5 — TEMKİNLİ VAZGEÇİŞ",
            "kisa_ad": "Temkinli Vazgeçiş",
            "emoji": "🚶",
            "renk": "#232b38",
            "vurgu": "#94a3b8",
            "resim": "son_5.png",
            "metin": "Şartları veya cihazı kendine uygun bulmadın ve paranı cebinde tutarak mağazadan kendi kararınla ayrıldın.",
            "ipucu": "Satın almadan mağazadan ayrılmayı seç."
        },
        "son_6": {
            "baslik": "SON 6 — UYANIK ALICI (KUSURU FIRSATA ÇEVİRDİN)",
            "kisa_ad": "Uyanık Alıcı (Tamir Fırsatı)",
            "emoji": "🛠️",
            "renk": "#382c14",
            "vurgu": "#fbbf24",
            "resim": "son_6.png",
            "metin": "İnceleme yaparak gizli kusuru yakaladın, bunu pazarlıkta koz olarak kullanıp fiyatı dip seviyeye kırdın ve kelepir fiyata kapattın!",
            "ipucu": "Gizli kusurlu bir cihazı incele, kusuru pazarlıkta koz olarak kullan ve ucuza satın al."
        },
        "son_7": {
            "baslik": "SON 7 — BAŞARILI PAZARLIK",
            "kisa_ad": "Başarılı Pazarlık",
            "emoji": "🤝",
            "renk": "#17304a",
            "vurgu": "#60a5fa",
            "resim": "son_7.png",
            "metin": "Pazarlık masasında sıkı durdun, etiket fiyatından indirim kopararak bütçeni koruyan karlı bir anlaşma yaptın.",
            "ipucu": "Fiyatı pazarlıkla düşürüp bütçeni aşmadan satın al (incelemeden veya orta güvenle)."
        },
        "son_8": {
            "baslik": "SON 8 — KAZAN-KAZAN (STANDART ANLAŞMA)",
            "kisa_ad": "Kazan-Kazan (Hızlı Anlaşma)",
            "emoji": "🎉",
            "renk": "#1b362e",
            "vurgu": "#4ade80",
            "resim": "son_8.png",
            "metin": "Pazarlıkla vakit kaybetmeden, bütçene uygun ve sağlam bir cihazı etiket fiyatından alıp satıcıyla el sıkıştın.",
            "ipucu": "Kusursuz bir cihazı fiyat kırmadan, bütçen yetiyorken doğrudan satın al."
        }
    }
}

def tl(amount: int) -> str:
    """8500 -> '8.500 TL'"""
    return f"{int(round(amount)):,}".replace(",", ".") + " TL"

class SoundManager:
    """Arayüzü dondurmadan arka planda ses efektleri çalar."""
    def __init__(self):
        self.enabled = True

    def play(self, effect: str):
        if not self.enabled or not HAS_WINSOUND:
            return
        threading.Thread(target=self._beep_worker, args=(effect,), daemon=True).start()

    def _beep_worker(self, effect: str):
        try:
            if effect == "kasa":  # Satın alma / Başarılı anlaşma
                for freq, dur in [(587, 90), (784, 90), (987, 110), (1175, 180)]:
                    winsound.Beep(freq, dur)
            elif effect == "uyari":  # Kusur bulundu / Düşük teklif / Kaba selam
                for freq, dur in [(360, 120), (280, 180)]:
                    winsound.Beep(freq, dur)
            elif effect == "kovulma":  # Sabır taştı / Kör alışveriş şoku
                for freq, dur in [(440, 110), (349, 120), (261, 240)]:
                    winsound.Beep(freq, dur)
            elif effect == "temiz":  # Temiz inceleme / Olumlu gelişme
                for freq, dur in [(659, 80), (880, 130)]:
                    winsound.Beep(freq, dur)
            elif effect == "yeni_son":  # Yeni son açıldı fanfarı
                for freq, dur in [(523, 80), (659, 80), (784, 80), (1046, 200)]:
                    winsound.Beep(freq, dur)
            elif effect == "tik":
                winsound.Beep(700, 45)
        except Exception:
            pass

class Game(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pazarlık Zamanı v2.0 | İkinci El Teknoloji Pazarı")
        self.geometry("1160x790")
        self.minsize(960, 680)
        self.configure(fg_color="#0b1220")

        self.sound = SoundManager()
        self.difficulty = "Normal"
        self._loaded_image = None
        self.records = self.load_records()

        self.reset_state()
        self.build_ui()
        self.start_game()

    # ------------------------------------------------------------------------
    # KAYIT SİSTEMİ (kayit.json)
    # ------------------------------------------------------------------------
    def load_records(self) -> dict:
        default_data = {
            "kesfedilen_sonlar": [],
            "en_yuksek_puan": 0,
            "toplam_oyun": 0,
            "son_puanlari": {}
        }
        if os.path.exists(KAYIT_DOSYASI):
            try:
                with open(KAYIT_DOSYASI, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    valid_endings = set(OYUN_AYARLARI["sonlar"].keys())
                    discovered = [s for s in data.get("kesfedilen_sonlar", []) if s in valid_endings]
                    default_data["kesfedilen_sonlar"] = discovered
                    default_data["en_yuksek_puan"] = int(data.get("en_yuksek_puan", 0))
                    default_data["toplam_oyun"] = int(data.get("toplam_oyun", 0))
                    if isinstance(data.get("son_puanlari"), dict):
                        default_data["son_puanlari"] = data["son_puanlari"]
            except Exception:
                pass
        return default_data

    def save_records(self):
        try:
            with open(KAYIT_DOSYASI, "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

    # ------------------------------------------------------------------------
    # OYUN DURUMU SIFIRLAMA
    # ------------------------------------------------------------------------
    def reset_state(self):
        zorluk_ayar = OYUN_AYARLARI["zorluklar"][self.difficulty]

        self.satici = random.choice(OYUN_AYARLARI["saticilar"])
        self.urun = random.choice(OYUN_AYARLARI["urunler"])

        if random.random() < zorluk_ayar["kusur_ihtimali"]:
            self.kusur = random.choice(OYUN_AYARLARI["kusurlar"])
        else:
            self.kusur = None

        self.start_price = self.urun["fiyat"]
        self.last_price = self.start_price

        # Başlangıç bütçesi zorluğa ve ürün fiyatına göre hesaplanır
        raw_budget = int(round((self.start_price * zorluk_ayar["butce_carpani"]) / 100.0) * 100)
        self.start_budget = raw_budget
        self.budget = raw_budget

        self.max_patience = max(2, self.satici["baz_sabir"] + zorluk_ayar["ek_sabir"])
        self.patience = self.max_patience

        self.trust = 50
        self.satisfaction = 50
        self.greeted = False
        self.inspected = False
        self.defect_known = False
        self.defect_used_in_bargain = False
        self.offer = None
        self.bargain_count = 0
        self.purchased = False
        self.kicked_out = False
        self.finished = False

    def current_price(self) -> int:
        return self.last_price

    # ------------------------------------------------------------------------
    # ARAYÜZ OLUŞTURMA
    # ------------------------------------------------------------------------
    def build_ui(self):
        self.grid_columnconfigure(0, weight=7)
        self.grid_columnconfigure(1, weight=5)
        self.grid_rowconfigure(1, weight=1)

        # ÜST BAŞLIK BAR
        header = ctk.CTkFrame(self, fg_color="#111c2e", corner_radius=18)
        header.grid(row=0, column=0, columnspan=2, padx=18, pady=(16, 10), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.grid(row=0, column=0, padx=20, pady=12, sticky="w")
        ctk.CTkLabel(
            title_box,
            text=OYUN_AYARLARI["magaza_adi"],
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#f3f7ff"
        ).pack(anchor="w")
        ctk.CTkLabel(
            title_box,
            text=OYUN_AYARLARI["magaza_alt_baslik"],
            font=ctk.CTkFont(size=12),
            text_color="#9fb0c8"
        ).pack(anchor="w", pady=(2, 0))

        # Üst sağ kontrol araçları (Zorluk, Ses, Sonlarım)
        controls = ctk.CTkFrame(header, fg_color="transparent")
        controls.grid(row=0, column=1, padx=18, pady=12, sticky="e")

        ctk.CTkLabel(controls, text="Zorluk:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#9fb0c8").pack(side="left", padx=(0, 6))
        self.diff_menu = ctk.CTkOptionMenu(
            controls,
            values=list(OYUN_AYARLARI["zorluklar"].keys()),
            command=self.change_difficulty,
            width=105,
            height=34,
            fg_color="#1e3a5f",
            button_color="#2563eb",
            button_hover_color="#1d4ed8"
        )
        self.diff_menu.set(self.difficulty)
        self.diff_menu.pack(side="left", padx=(0, 10))

        self.sound_btn = ctk.CTkButton(
            controls,
            text="🔊 Ses: Açık",
            command=self.toggle_sound,
            width=110,
            height=34,
            fg_color="#26364d",
            hover_color="#344964"
        )
        self.sound_btn.pack(side="left", padx=(0, 10))

        self.endings_btn = ctk.CTkButton(
            controls,
            text="🏆 Sonlarım (0/8)",
            command=self.open_endings_modal,
            width=150,
            height=34,
            fg_color="#b45309",
            hover_color="#92400e",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.endings_btn.pack(side="left")

        # SOL PANEL: GÖRSEL SAHNE ALANI + DİYALOG + SEÇİMLER
        left = ctk.CTkFrame(self, fg_color="#111c2e", corner_radius=18)
        left.grid(row=1, column=0, padx=(18, 9), pady=(0, 16), sticky="nsew")
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(1, weight=1)

        # 1. DEĞİŞEN GÖRSEL SAHNE BANNER ALANI + SATICI YÜZ İFADESİ KARTI
        stage_container = ctk.CTkFrame(left, fg_color="transparent")
        stage_container.grid(row=0, column=0, padx=18, pady=(16, 8), sticky="ew")
        stage_container.grid_columnconfigure(0, weight=3)
        stage_container.grid_columnconfigure(1, weight=2)

        # Sahne görsel kartı
        self.visual_banner = ctk.CTkFrame(stage_container, fg_color="#132338", corner_radius=14, border_width=2, border_color="#38bdf8")
        self.visual_banner.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        self.scene_emoji_label = ctk.CTkLabel(
            self.visual_banner,
            text="🏪",
            font=ctk.CTkFont(size=42)
        )
        self.scene_emoji_label.pack(pady=(12, 2))

        self.scene_title_label = ctk.CTkLabel(
            self.visual_banner,
            text="Mağazaya Giriş",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#f8fafc"
        )
        self.scene_title_label.pack(padx=12)

        self.scene_sub_label = ctk.CTkLabel(
            self.visual_banner,
            text="Dükkana adım attın.",
            font=ctk.CTkFont(size=12),
            text_color="#cbd5e1",
            wraplength=360
        )
        self.scene_sub_label.pack(padx=12, pady=(2, 12))

        # Satıcının güvene göre değişen yüz ifadesi kartı
        self.seller_card = ctk.CTkFrame(stage_container, fg_color="#172439", corner_radius=14, border_width=1, border_color="#2b3f5c")
        self.seller_card.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        self.seller_face_label = ctk.CTkLabel(
            self.seller_card,
            text="🙂",
            font=ctk.CTkFont(size=38)
        )
        self.seller_face_label.pack(pady=(10, 2))

        self.seller_name_label = ctk.CTkLabel(
            self.seller_card,
            text="Satıcı",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#f1f5f9"
        )
        self.seller_name_label.pack(padx=10)

        self.seller_mood_label = ctk.CTkLabel(
            self.seller_card,
            text="İfade: Normal / İlgili",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#60a5fa"
        )
        self.seller_mood_label.pack(padx=10, pady=(2, 2))

        self.patience_label = ctk.CTkLabel(
            self.seller_card,
            text="Sabır: ❤️❤️❤️",
            font=ctk.CTkFont(size=12),
            text_color="#fda4af"
        )
        self.patience_label.pack(padx=10, pady=(0, 10))

        # Diyalog geçmişi kutusu
        self.log = ctk.CTkTextbox(
            left,
            wrap="word",
            corner_radius=12,
            fg_color="#0b1424",
            text_color="#e4ebf5",
            font=ctk.CTkFont(size=13),
            border_width=1,
            border_color="#25354d"
        )
        self.log.grid(row=1, column=0, padx=18, pady=6, sticky="nsew")
        self.log.configure(state="disabled")

        # Seçenek butonları alanı
        self.choices = ctk.CTkFrame(left, fg_color="transparent")
        self.choices.grid(row=2, column=0, padx=18, pady=(6, 16), sticky="ew")
        self.choices.grid_columnconfigure(0, weight=1)

        # SAĞ PANEL: ÜRÜN KARTI, İSTATİSTİKLER, REKOR & KONTROLLER
        right = ctk.CTkFrame(self, fg_color="#111c2e", corner_radius=18)
        right.grid(row=1, column=1, padx=(9, 18), pady=(0, 16), sticky="nsew")
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            right,
            text="TEZGAHTAKİ CİHAZ & ALIŞVERİŞ ÖZETİ",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#8da4c4"
        ).grid(row=0, column=0, padx=18, pady=(16, 8), sticky="w")

        # Ürün bilgi kartı
        product = ctk.CTkFrame(right, fg_color="#1b2a40", corner_radius=14, border_width=1, border_color="#2e4566")
        product.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="ew")

        self.prod_title_label = ctk.CTkLabel(
            product,
            text="📱 İkinci El Akıllı Telefon",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#f8fafc"
        )
        self.prod_title_label.pack(anchor="w", padx=15, pady=(12, 3))

        self.prod_desc_label = ctk.CTkLabel(
            product,
            text="Durum: İyi · Kutulu",
            font=ctk.CTkFont(size=12),
            text_color="#b9c8dc"
        )
        self.prod_desc_label.pack(anchor="w", padx=15, pady=(0, 3))

        self.prod_defect_badge = ctk.CTkLabel(
            product,
            text="🔎 İnceleme Durumu: Henüz kontrol edilmedi",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#fbbf24"
        )
        self.prod_defect_badge.pack(anchor="w", padx=15, pady=(0, 4))

        self.prod_price_label = ctk.CTkLabel(
            product,
            text="Etiket fiyatı: 8.500 TL",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#38bdf8"
        )
        self.prod_price_label.pack(anchor="w", padx=15, pady=(0, 12))

        # İstatistik Kartları
        self.budget_label = self.stat(right, 2, "💰 Kalan Bütçe", tl(self.budget))
        self.trust_label = self.stat(right, 3, "🤝 Satıcının Güveni", "50 / 100")
        self.satisfaction_label = self.stat(right, 4, "😊 Alıcı Memnuniyeti", "50 / 100")

        # Koleksiyon ve En Yüksek Puan Özeti Kartı
        progress_card = ctk.CTkFrame(right, fg_color="#152236", corner_radius=12, border_width=1, border_color="#243854")
        progress_card.grid(row=5, column=0, padx=15, pady=(6, 10), sticky="ew")

        self.record_score_label = ctk.CTkLabel(
            progress_card,
            text="🏆 En Yüksek Puan: 0 / 100",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#fbbf24"
        )
        self.record_score_label.pack(anchor="w", padx=12, pady=(10, 2))

        self.record_endings_label = ctk.CTkLabel(
            progress_card,
            text="📚 Keşfedilen Sonlar: 8 sondan 0'ına ulaştın",
            font=ctk.CTkFont(size=12),
            text_color="#cbd5e1"
        )
        self.record_endings_label.pack(anchor="w", padx=12, pady=(0, 6))

        self.endings_progress_bar = ctk.CTkProgressBar(progress_card, height=10, corner_radius=5, progress_color="#f59e0b")
        self.endings_progress_bar.pack(fill="x", padx=12, pady=(0, 10))
        self.endings_progress_bar.set(0)

        # Alt Butonlar
        btn_row = ctk.CTkFrame(right, fg_color="transparent")
        btn_row.grid(row=6, column=0, padx=15, pady=(4, 14), sticky="ew")
        btn_row.grid_columnconfigure(0, weight=1)
        btn_row.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            btn_row,
            text="↻ Yeni Oyun / Başka Cihaz",
            command=self.restart,
            height=38,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, padx=(0, 5), sticky="ew")

        ctk.CTkButton(
            btn_row,
            text="🏆 Sonlarım & Rekor",
            command=self.open_endings_modal,
            height=38,
            fg_color="#26364d",
            hover_color="#344964",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def stat(self, parent, row, title, value):
        card = ctk.CTkFrame(parent, fg_color="#172439", corner_radius=12)
        card.grid(row=row, column=0, padx=15, pady=4, sticky="ew")
        ctk.CTkLabel(card, text=title, text_color="#9fb0c8", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=12, pady=(7, 0))
        label = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=17, weight="bold"))
        label.pack(anchor="w", padx=12, pady=(0, 7))
        return label

    # ------------------------------------------------------------------------
    # GÖRSEL SAHNE VE SATICI İFADESİ GÜNCELLEME
    # ------------------------------------------------------------------------
    def update_scene_visual(self, scene_key: str, is_ending: bool = False):
        data = OYUN_AYARLARI["sonlar"][scene_key] if is_ending else OYUN_AYARLARI["sahneler"][scene_key]
        bg_color = data.get("renk", "#132338")
        border_color = data.get("vurgu", "#38bdf8")
        emoji_text = data.get("emoji", "🏪")
        title_text = data.get("baslik", "")
        sub_text = data.get("metin" if is_ending else "alt_yazi", "")
        img_name = data.get("resim", "")

        self.visual_banner.configure(fg_color=bg_color, border_color=border_color)
        self.scene_title_label.configure(text=title_text, text_color="#ffffff")
        self.scene_sub_label.configure(text=sub_text)

        # Eğer images/ klasöründe ilgili PNG varsa onu yükle, yoksa büyük Emoji sahnesi göster
        img_path = os.path.join(GORSEL_KLASORU, img_name) if img_name else ""
        if img_path and os.path.exists(img_path):
            if HAS_PIL:
                try:
                    pil_img = Image.open(img_path)
                    self._loaded_image = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(96, 72))
                    self.scene_emoji_label.configure(image=self._loaded_image, text="")
                    return
                except Exception:
                    pass
            else:
                try:
                    self._loaded_image = tk.PhotoImage(file=img_path)
                    self.scene_emoji_label.configure(image=self._loaded_image, text="")
                    return
                except Exception:
                    pass

        self.scene_emoji_label.configure(image=None, text=emoji_text)

    def update_seller_face(self):
        """Satıcının yüz ifadesi güvene ve kalan sabra göre canlı değişir."""
        trust = max(0, min(100, self.trust))
        if self.kicked_out or self.patience <= 0:
            face = "🤬"
            mood = "İfade: Küplere Bindi!"
            color = "#ef4444"
            card_bg = "#3b151c"
        elif self.patience == 1 or trust < 30:
            face = "😠"
            mood = "İfade: Kaşları Çatık"
            color = "#f97316"
            card_bg = "#331c19"
        elif trust < 50:
            face = "😒"
            mood = "İfade: Ciddi & Mesafeli"
            color = "#fbbf24"
            card_bg = "#2b2418"
        elif trust < 72:
            face = "🙂"
            mood = "İfade: Normal & İlgili"
            color = "#60a5fa"
            card_bg = "#172439"
        else:
            face = "😄"
            mood = "İfade: Gülen Yüz (Samimi)"
            color = "#34d399"
            card_bg = "#132e26"

        hearts = "❤️" * max(0, self.patience) + "🖤" * max(0, self.max_patience - max(0, self.patience))
        self.seller_card.configure(fg_color=card_bg)
        self.seller_face_label.configure(text=face)
        self.seller_name_label.configure(text=f"{self.satici['ad']} ({self.satici['unvan']})")
        self.seller_mood_label.configure(text=mood, text_color=color)
        self.patience_label.configure(text=f"Sabır: {hearts} ({max(0, self.patience)}/{self.max_patience})")

    def update_stats(self):
        self.budget_label.configure(text=tl(self.budget))
        self.trust_label.configure(text=f"{max(0, min(100, self.trust))} / 100")
        self.satisfaction_label.configure(text=f"{max(0, min(100, self.satisfaction))} / 100")

        # Ürün bilgilerini güncelle
        self.prod_title_label.configure(text=f"{self.urun['ikon']}  {self.urun['ad']}")
        self.prod_desc_label.configure(text=self.urun["vitrin_bilgisi"])

        if not self.inspected:
            self.prod_defect_badge.configure(
                text="🔎 İnceleme: Henüz kontrol edilmedi (Gizli kusur olabilir!)",
                text_color="#fbbf24"
            )
        elif self.kusur:
            self.prod_defect_badge.configure(
                text=f"⚠️ Tespit: {self.kusur['baslik']}",
                text_color="#f87171"
            )
        else:
            self.prod_defect_badge.configure(
                text="✅ İnceleme: Cihaz tamamen kusursuz ve temiz!",
                text_color="#34d399"
            )

        if self.last_price < self.start_price:
            self.prod_price_label.configure(
                text=f"Etiket: {tl(self.start_price)}  ➔  Güncel Fiyat: {tl(self.last_price)}",
                text_color="#4ade80"
            )
        else:
            self.prod_price_label.configure(
                text=f"Etiket Fiyatı: {tl(self.start_price)}",
                text_color="#38bdf8"
            )

        # Kayıt ve son ilerlemesi
        total_endings = len(OYUN_AYARLARI["sonlar"])
        found_count = len(self.records["kesfedilen_sonlar"])
        self.endings_btn.configure(text=f"🏆 Sonlarım ({found_count}/{total_endings})")
        self.record_score_label.configure(text=f"🏆 En Yüksek Puan: {self.records['en_yuksek_puan']} / 100")
        self.record_endings_label.configure(
            text=f"📚 Keşfedilen Sonlar: {total_endings} sondan {found_count}'ine ulaştın"
        )
        self.endings_progress_bar.set(found_count / max(1, total_endings))

        self.update_seller_face()

    # ------------------------------------------------------------------------
    # YARDIMCI METOTLAR
    # ------------------------------------------------------------------------
    def say(self, who: str, text: str):
        self.log.configure(state="normal")
        self.log.insert("end", f"{who}\n{text}\n\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def clear_choices(self):
        for child in self.choices.winfo_children():
            child.destroy()

    def choice(self, text: str, command, style: str = "primary"):
        colors = {
            "primary": ("#2563eb", "#1d4ed8"),
            "success": ("#059669", "#047857"),
            "warning": ("#d97706", "#b45309"),
            "danger": ("#dc2626", "#b91c1c"),
            "secondary": ("#26364d", "#344964"),
        }
        fg, hover = colors.get(style, colors["primary"])
        ctk.CTkButton(
            self.choices,
            text=text,
            command=command,
            height=38,
            anchor="w",
            corner_radius=10,
            fg_color=fg,
            hover_color=hover,
            font=ctk.CTkFont(size=13, weight="bold" if style != "secondary" else "normal")
        ).pack(fill="x", pady=3)

    def toggle_sound(self):
        self.sound.enabled = not self.sound.enabled
        self.sound_btn.configure(text="🔊 Ses: Açık" if self.sound.enabled else "🔇 Ses: Kapalı")
        if self.sound.enabled:
            self.sound.play("tik")

    def change_difficulty(self, new_diff: str):
        if new_diff != self.difficulty:
            self.difficulty = new_diff
            self.restart()

    # ------------------------------------------------------------------------
    # OYUN AKIŞI — 1. ADIM: MAĞAZAYA GİRİŞ VE SELAMLAŞMA (deneme_1.py entegrasyonu)
    # ------------------------------------------------------------------------
    def start_game(self):
        self.update_scene_visual("giris")
        self.update_stats()
        zorluk_bilgi = OYUN_AYARLARI["zorluklar"][self.difficulty]["aciklama"]
        self.say(
            "📍 Mağazaya Giriş",
            f"Dükkana adımını attın. Tezgahta {self.satici['ad']} ({self.satici['unvan']}) var. {self.satici['karsilama']}\n"
            f"Vitrindeki cihaz: {self.urun['ad']} — Etiket fiyatı: {tl(self.start_price)} | Bütçen: {tl(self.budget)}\n"
            f"[Zorluk: {self.difficulty} — {zorluk_bilgi}]"
        )
        self.show_greeting_choices()

    def show_greeting_choices(self):
        self.clear_choices()
        self.choice(
            f"👋  'Selamünaleyküm {self.satici['ad']}, kolay gelsin! Hayırlı işler.' (Sıcak ve saygılı selam)",
            lambda: self.handle_greeting("saygili"),
            "success"
        )
        self.choice(
            "🤝  'Merhaba, iyi günler. Kolay gelsin.' (Kibar ve standart giriş)",
            lambda: self.handle_greeting("normal"),
            "primary"
        )
        self.choice(
            f"💬  (Selam vermeden) 'Şu {tl(self.start_price)}'lik cihaza bakacaktım, en son kaça olur?'",
            lambda: self.handle_greeting("kaba"),
            "secondary"
        )

    def handle_greeting(self, attitude: str):
        if self.finished:
            return
        self.greeted = True
        cevap = self.satici["selam_cevap"][attitude]

        if attitude == "saygili":
            self.trust = min(100, self.trust + 15)
            self.satisfaction = min(100, self.satisfaction + 6)
            self.say("Sen · Alıcı", f"Selamünaleyküm {self.satici['ad']}, kolay gelsin! Hayırlı işler.")
            self.say(self.satici["ad"], cevap)
            self.say("💡 Oyun Notu", "Esnafa sıcak ve saygılı yaklaştın. Satıcının yüzü güldü, pazarlık kredin arttı! (+15 Güven)")
            self.sound.play("temiz")
        elif attitude == "normal":
            self.trust = min(100, self.trust + 5)
            self.say("Sen · Alıcı", "Merhaba, iyi günler. Kolay gelsin.")
            self.say(self.satici["ad"], cevap)
            self.say("💡 Oyun Notu", "Doğal ve kibar bir giriş yaptın. (+5 Güven)")
            self.sound.play("tik")
        else:
            self.trust = max(0, self.trust - 16)
            self.satisfaction = max(0, self.satisfaction - 5)
            if self.satici["ad"] == "İnatçı Kazım":
                self.patience = max(1, self.patience - 1)
            self.say("Sen · Alıcı", f"Direkt şu {tl(self.start_price)}'lik cihaza bakacaktım, en son kaça bırakırsın?")
            self.say(self.satici["ad"], cevap)
            self.say("⚠️ Oyun Notu", "Selam vermeden fiyata dalmak esnafın hoşuna gitmedi, kaşları çatıldı! (-16 Güven)")
            self.sound.play("uyari")

        self.update_scene_visual("vitrin")
        self.update_stats()
        self.show_main_choices()

    # ------------------------------------------------------------------------
    # OYUN AKIŞI — 2. ADIM: ANA SEÇENEKLER
    # ------------------------------------------------------------------------
    def show_main_choices(self):
        if self.finished:
            return
        self.clear_choices()
        price = self.current_price()

        if not self.inspected:
            self.choice("🔎  Cihazı detaylı incele (Ekran, batarya, anakart ve hesap kontrolü)", self.inspect, "primary")
        else:
            self.choice("🔎  İnceleme raporunu tekrar gözden geçir", self.inspect, "secondary")

        self.choice(f"🤝  Fiyat için pazarlık masasına otur (Kalan Sabır: {self.patience} ❤️)", self.bargain, "warning")

        if not self.inspected:
            self.choice(f"💳  İncelemeden {tl(price)}'ye hemen satın al (Kör Alışveriş Riski!)", self.buy_blind, "danger")
        else:
            self.choice(f"💳  {tl(price)} fiyatla satın alma ekranına geç", self.purchase_options, "success")

        self.choice("🚪  Teşekkür edip mağazadan ayrıl", self.leave, "secondary")

    # ------------------------------------------------------------------------
    # OYUN AKIŞI — 3. ADIM: CİHAZI İNCELEME & GİZLİ KUSUR TESPİTİ
    # ------------------------------------------------------------------------
    def inspect(self):
        if self.finished:
            return
        self.say("Sen · Alıcı", "Cihazın pil sağlığını, ekran dokunmatiğini, kamerasını ve hesap durumunu kontrol edebilir miyim?")

        if not self.inspected:
            self.inspected = True
            # Teknoloji Kurdu Mert inceleyen müşteriye ekstra güven duyar
            trust_bonus = 16 if self.satici["ad"] == "Teknoloji Kurdu Mert" else 10
            self.trust = min(100, self.trust + trust_bonus)
            self.satisfaction = min(100, self.satisfaction + 8)

            if self.kusur:
                self.defect_known = True
                self.update_scene_visual("inceleme_kusurlu")
                self.say(self.satici["ad"], "Tabii, buyur bak. Bildiğim kadarıyla temiz cihaz...")
                self.say(
                    "⚠️ GİZLİ KUSUR TESPİT EDİLDİ!",
                    f"Problem: {self.kusur['baslik']}\n"
                    f"Detay: {self.kusur['inceleme_metni']}\n"
                    f"İpucu: Bu kusuru pazarlıkta koz olarak kullanıp fiyatı dip seviyeye indirebilir veya cihazdan vazgeçebilirsin!"
                )
                self.sound.play("uyari")
            else:
                self.update_scene_visual("inceleme_temiz")
                self.say(
                    self.satici["ad"],
                    "Tabii, gönül rahatlığıyla test et. Her türlü kontrole açık."
                )
                self.say(
                    "✅ İNCELEME SONUCU: KUSURSUZ",
                    "Batarya voltajı, ekran pikselleri, kamera odaklaması ve bulut hesabı tamamen temiz çıktı! "
                    f"Bilinçli yaklaşımın satıcının güvenini artırdı (+{trust_bonus} Güven)."
                )
                self.sound.play("temiz")
        else:
            if self.kusur:
                self.say("🔎 İnceleme Özeti", f"Daha önce tespit ettiğin kusur: {self.kusur['baslik']}. Pazarlıkta koz olarak kullanabilirsin.")
            else:
                self.say("🔎 İnceleme Özeti", "Cihazı zaten detaylıca kontrol ettin, hiçbir gizli kusuru yok.")

        self.update_stats()
        self.clear_choices()
        if self.kusur and not self.defect_used_in_bargain:
            self.choice(f"⚡  Bulduğun kusuru ({self.kusur['baslik']}) gösterip büyük indirim iste!", lambda: self.make_offer("kusur_kozu"), "warning")
        self.choice("🤝  Fiyat pazarlığı yap", self.bargain, "primary")
        self.choice(f"💳  {tl(self.current_price())} fiyatla satın almayı değerlendir", self.purchase_options, "success")
        self.choice("🚪  Bu cihaz bana uymadı, mağazadan ayrıl", self.leave, "secondary")

    # ------------------------------------------------------------------------
    # OYUN AKIŞI — 4. ADIM: PAZARLIK SİSTEMİ & SABIR MEKANİĞİ
    # ------------------------------------------------------------------------
    def bargain(self):
        if self.finished:
            return
        self.update_scene_visual("pazarlik")
        self.update_stats()

        cur = self.current_price()
        dip = self.urun["dip_fiyat"]

        # Cihaz fiyatına göre dinamik teklif basamakları
        makul_teklif = int(round((cur * 0.91) / 100.0) * 100)
        siki_teklif = int(round((max(dip * 0.96, cur * 0.82)) / 100.0) * 100)
        olucu_teklif = int(round((dip * 0.78) / 100.0) * 100)

        # Tekliflerin güncel fiyattan düşük olmasını garanti et
        makul_teklif = min(makul_teklif, cur - 200)
        siki_teklif = min(siki_teklif, makul_teklif - 300)
        olucu_teklif = min(olucu_teklif, siki_teklif - 500)

        self.clear_choices()

        if self.defect_known and self.kusur and not self.defect_used_in_bargain:
            self.choice(
                f"⚡  Kusuru Koz Olarak Kullan: '{self.kusur['baslik']}' masrafını düşelim!",
                lambda: self.make_offer("kusur_kozu"),
                "warning"
            )

        self.choice(
            f"🎯  Makul Teklif Ver: {tl(makul_teklif)} (Güveni korur, orta yolu bulur)",
            lambda: self.make_offer("makul", makul_teklif),
            "primary"
        )
        self.choice(
            f"🔥  Sıkı Pazarlık Yap: {tl(siki_teklif)} (Ciddi indirim ister, güven önemli)",
            lambda: self.make_offer("siki", siki_teklif),
            "success"
        )
        self.choice(
            f"💀  Ölücü Teklifi Yap: {tl(olucu_teklif)} (Çok riskli! Satıcıyı kızdırabilir)",
            lambda: self.make_offer("olucu", olucu_teklif),
            "danger"
        )

        # Serbest fiyat teklifi giriş satırı
        custom_row = ctk.CTkFrame(self.choices, fg_color="transparent")
        custom_row.pack(fill="x", pady=3)
        custom_row.grid_columnconfigure(0, weight=1)

        custom_entry = ctk.CTkEntry(
            custom_row,
            placeholder_text=f"Kendi teklifini yaz (Örn: {siki_teklif})...",
            height=36,
            fg_color="#0b1424",
            border_color="#3b82f6"
        )
        custom_entry.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        def gonder_ozel_teklif():
            metin = custom_entry.get().strip().replace(".", "").replace(",", "").replace("TL", "").replace("tl", "").strip()
            if not metin.isdigit():
                self.say("⚠️ Uyarı", "Lütfen geçerli bir sayısal fiyat teklifi girin (Örn: 7500).")
                self.sound.play("uyari")
                return
            tutar = int(metin)
            if tutar <= 0:
                return
            if tutar >= cur:
                self.say("Sen · Alıcı", f"{tl(tutar)} veriyorum, hemen sar!")
                self.say(self.satici["ad"], f"Zaten istediğim fiyat {tl(cur)} idi, memnuniyetle!")
                self.complete_purchase(cur)
            elif tutar >= makul_teklif:
                self.make_offer("makul", tutar)
            elif tutar >= int(dip * 0.90):
                self.make_offer("siki", tutar)
            else:
                self.make_offer("olucu", tutar)

        ctk.CTkButton(
            custom_row,
            text="✍️ Özel Teklif Ver",
            command=gonder_ozel_teklif,
            height=36,
            width=145,
            fg_color="#4f46e5",
            hover_color="#4338ca",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=1, sticky="e")

        self.choice(
            f"💳  Pazarlığı bırak, {tl(cur)} son fiyattan satın alma ekranına geç",
            self.purchase_options,
            "secondary"
        )
        self.choice("🚪  Anlaşamadık, mağazadan ayrıl", self.leave, "secondary")

    def make_offer(self, offer_type: str, amount: int = 0):
        if self.finished:
            return

        self.bargain_count += 1
        esneklik = self.satici["esneklik"]
        dip = self.urun["dip_fiyat"]

        # 1) KUSUR KOZU KULLANIMI (Sabır düşürmez, aksine haklı indirim sağlar!)
        if offer_type == "kusur_kozu" and self.kusur:
            self.defect_used_in_bargain = True
            self.offer = "kusur_kozu"
            indirim = int(round((self.start_price * self.kusur["ek_indirim_orani"] * esneklik) / 100.0) * 100)
            ozel_dip = int(round((dip * 0.85) / 100.0) * 100)
            yeni_fiyat = max(ozel_dip, self.last_price - max(600, indirim))
            self.last_price = yeni_fiyat
            self.trust = min(100, self.trust + 6)
            self.satisfaction = min(100, self.satisfaction + 14)

            self.say("Sen · Alıcı", self.kusur["pazarlik_kozu"])
            self.say(
                self.satici["ad"],
                f"Valla dikkatli çıktın, o kusuru ben de yeni fark ettim... Tamir masrafı senin olsun, fiyatı {tl(self.last_price)}'ye çekiyorum!"
            )
            self.say("💡 Oyun Notu", f"Gizli kusuru yakalayıp masaya koyduğun için satıcı {tl(self.last_price)} fiyata indi!")
            self.sound.play("temiz")

        # 2) MAKUL TEKLİF
        elif offer_type == "makul":
            self.patience -= 1
            self.offer = amount
            self.say("Sen · Alıcı", f"Bütçemi zorlamak istemiyorum, {tl(amount)} verirsem el sıkışır mıyız?")

            if self.patience <= 0:
                self.trigger_kickout()
                return

            self.trust = min(100, self.trust + 5)
            self.satisfaction = min(100, self.satisfaction + 5)
            guven_bonus = 1.15 if self.trust >= 65 else 0.95
            indirim = int(round(((self.last_price - amount) * 0.65 * esneklik * guven_bonus) / 100.0) * 100)
            yeni_fiyat = max(dip, self.last_price - max(200, indirim))

            if yeni_fiyat < self.last_price:
                self.last_price = yeni_fiyat
                self.say(self.satici["ad"], f"Seni kırmayayım, orta yolu bulalım. {tl(self.last_price)} olsun, hayrını gör.")
                self.sound.play("temiz")
            else:
                self.say(self.satici["ad"], f"İnan kurtarmaz, zaten dip fiyata indim. Son {tl(self.last_price)} olur.")
                self.sound.play("uyari")

        # 3) SIKI PAZARLIK
        elif offer_type == "siki":
            self.patience -= 1
            self.offer = amount
            self.say("Sen · Alıcı", f"Nakit ve peşin alacağım, {tl(amount)} yaparsan hemen şimdi sarıp alayım.")

            if self.patience <= 0:
                self.trigger_kickout()
                return

            if self.trust >= 60:
                indirim = int(round(((self.last_price - amount) * 0.75 * esneklik) / 100.0) * 100)
                self.last_price = max(dip, self.last_price - max(300, indirim))
                self.satisfaction = min(100, self.satisfaction + 8)
                self.say(self.satici["ad"], f"Muhabbetin hoşuma gitti, esnaf adamsın. Senin hatırına {tl(self.last_price)} yapıyorum!")
                self.sound.play("temiz")
            else:
                self.trust = max(0, self.trust - 6)
                indirim = int(round(((self.last_price - amount) * 0.40 * esneklik) / 100.0) * 100)
                self.last_price = max(dip + 200, self.last_price - max(100, indirim))
                self.say(self.satici["ad"], f"O kadar da inemem, malımın arkasındayım. En son {tl(self.last_price)} olur, zorlama.")
                self.sound.play("uyari")

        # 4) ÖLÜCÜ TEKLİFİ (ÇOK RİSKLİ)
        else:
            # Ölücü teklif sinirli satıcıda 2 sabır birden götürür!
            sabir_kaybi = 2 if self.satici["ad"] == "İnatçı Kazım" else 1
            self.patience -= sabir_kaybi
            self.offer = amount
            self.trust = max(0, self.trust - 18)
            self.satisfaction = max(0, self.satisfaction - 4)
            self.say("Sen · Alıcı", f"Piyasa durgun ustam, {tl(amount)} veririm, fazlası çıkmaz benden.")

            if self.patience <= 0:
                self.trigger_kickout()
                return

            self.last_price = max(dip + 300, self.last_price - 100)
            self.say(
                self.satici["ad"],
                f"Yok artık, bedavaya verseydik! Ölücülük yapma kardeşim, son fiyat {tl(self.last_price)}, bir kuruş daha inmem!"
            )
            self.say("⚠️ Oyun Notu", "Çok düşük teklif satıcıyı kızdırdı! Güveni ve sabrı hızla eridi.")
            self.sound.play("uyari")

        self.update_stats()
        self.clear_choices()
        self.choice(f"✅  {tl(self.last_price)} karşı teklifi kabul et ve satın al", lambda: self.complete_purchase(self.last_price), "success")
        self.choice(f"🤝  Bir tur daha pazarlık dene (Kalan Sabır: {self.patience} ❤️)", self.bargain, "warning")
        if not self.inspected:
            self.choice("🔎  Karar vermeden önce cihazı incele", self.inspect, "primary")
        self.choice("🚪  Anlaşamadık, mağazadan ayrıl", self.leave, "secondary")

    def trigger_kickout(self):
        """Satıcının sabrı sıfırlandığında tetiklenen kovulma sonu (son_4)."""
        self.kicked_out = True
        self.patience = 0
        self.trust = max(0, self.trust - 20)
        self.satisfaction = max(0, self.satisfaction - 15)
        self.say(
            self.satici["ad"],
            "Yeter artık kardeşim! Sabahtan beri fiyat kırıp duruyorsun, satmıyorum sana cihaz falan! Hadi başka dükkana!"
        )
        self.sound.play("kovulma")
        self.update_stats()
        self.finish(forced_ending="son_4")

    # ------------------------------------------------------------------------
    # OYUN AKIŞI — 5. ADIM: SATIN ALMA VEYA AYRILMA
    # ------------------------------------------------------------------------
    def purchase_options(self):
        if self.finished:
            return
        self.clear_choices()
        price = self.current_price()
        self.say(self.satici["ad"], f"Cihazın son fiyatı {tl(price)}. Ne diyorsun, sarayım mı?")

        if price <= self.budget:
            self.choice(f"💳  {tl(price)} ödeyerek satın al (Kalan bütçe: {tl(self.budget - price)})", lambda: self.complete_purchase(price), "success")
        else:
            fark = price - self.budget
            self.choice(
                f"💸  Bütçemi {tl(fark)} aşarak (borca girip) {tl(price)}'ye satın al",
                lambda: self.complete_purchase(price),
                "danger"
            )

        self.choice(f"🤝  Tekrar pazarlık masasına dön (Sabır: {self.patience} ❤️)", self.bargain, "warning")
        if not self.inspected:
            self.choice("🔎  Ödeme yapmadan önce cihazı incele", self.inspect, "primary")
        self.choice("🚪  Vazgeç ve mağazadan ayrıl", self.leave, "secondary")

    def buy_blind(self):
        if self.finished:
            return
        price = self.current_price()
        self.say("Sen · Alıcı", "Cihazı incelemeye gerek yok, temiz duruyor. Hemen alıyorum.")
        self.say(self.satici["ad"], "Tabii, hemen ödemeyi alıp kutusunu teslim edeyim.")
        self.satisfaction = max(0, self.satisfaction - 8)
        self.complete_purchase(price)

    def complete_purchase(self, price: int):
        if self.finished:
            return
        overspend = price > self.budget
        self.purchased = True
        self.budget -= price

        if overspend:
            self.satisfaction = max(0, self.satisfaction - 22)
            self.say("Sen · Alıcı", "Bütçemi aşıyor ama yine de karttan çekelim, kabul ediyorum.")
        else:
            tasarruf = self.start_price - price
            bonus = min(18, max(6, tasarruf // 150))
            self.satisfaction = min(100, self.satisfaction + bonus)

        self.say(self.satici["ad"], "Hayırlı uğurlu olsun, güle güle kullanın!")
        self.update_stats()
        self.finish()

    def leave(self):
        if self.finished:
            return
        self.say("Sen · Alıcı", "Teşekkür ederim, şimdilik satın almaktan vazgeçiyorum. İyi işler dilerim.")
        self.say(self.satici["ad"], "Rica ederim, kısmet. Fikriniz değişirse yine bekleriz.")
        self.sound.play("tik")
        self.finish(forced_ending="son_5")

    # ------------------------------------------------------------------------
    # OYUN SONU HESAPLAMA VE KAYIT (8 FARKLI SON)
    # ------------------------------------------------------------------------
    def finish(self, forced_ending: str = None):
        self.finished = True
        self.clear_choices()

        trust = max(0, min(100, self.trust))
        satisfaction = max(0, min(100, self.satisfaction))
        bargained = self.last_price < self.start_price

        # Hangi sona ulaşıldığını belirle
        if forced_ending:
            son_id = forced_ending
        elif not self.purchased:
            son_id = "son_5"  # Temkinli Vazgeçiş
        elif not self.inspected and self.kusur is not None:
            # İncelemeden kusurlu cihazı aldı -> Kör Alışveriş Şoku!
            self.satisfaction = max(0, self.satisfaction - 30)
            satisfaction = self.satisfaction
            son_id = "son_3"
        elif self.budget < 0 or satisfaction < 38:
            # Bütçeyi aştı veya çok düşük memnuniyet -> Kazıklandın & Bütçe Aşımı
            son_id = "son_2"
        elif self.inspected and self.kusur is not None and (self.defect_used_in_bargain or bargained):
            # Kusuru inceleyip buldu ve fiyatı kırdı -> Uyanık Alıcı!
            son_id = "son_6"
        elif self.inspected and self.kusur is not None and not bargained:
            # Kusuru gördü ama hiç indirim almadan tam fiyata aldı -> Kazıklandın
            son_id = "son_2"
        elif self.inspected and self.kusur is None and bargained and trust >= 60:
            # Kusursuz cihazı inceledi + iyi güven + pazarlık -> Kusursuz Kazanç (Usta Alıcı)
            son_id = "son_1"
        elif bargained:
            # Pazarlıkla indirim aldı -> Başarılı Pazarlık
            son_id = "son_7"
        else:
            # İndirimsiz ama bütçe dahilinde sorunsuz aldı -> Kazan-Kazan (Standart Anlaşma)
            son_id = "son_8"

        son_bilgi = OYUN_AYARLARI["sonlar"][son_id]

        # Puan hesaplama (Zorluk çarpanı ve strateji bonusları dahil)
        zorluk_carpani = OYUN_AYARLARI["zorluklar"][self.difficulty]["puan_carpani"]
        butce_puani = 45 if self.budget >= 0 else -15
        indirim_orani = max(0.0, (self.start_price - self.last_price) / max(1, self.start_price))
        indirim_puani = round(indirim_orani * 80) if self.purchased else 0
        inceleme_puani = 15 if self.inspected else 0

        ham_puan = (trust * 0.32) + (satisfaction * 0.38) + (butce_puani * 0.4) + indirim_puani + inceleme_puani
        if son_id in ("son_3", "son_4"):
            ham_puan = min(35, ham_puan * 0.45)
        elif son_id == "son_2":
            ham_puan = min(48, ham_puan * 0.60)
        elif son_id == "son_5":
            ham_puan = min(68, (trust * 0.35) + 32 + (10 if self.inspected and self.kusur else 0))

        score = max(0, min(100, int(round(ham_puan * zorluk_carpani))))

        # Ses efekti ve sahne görseli
        self.update_scene_visual(son_id, is_ending=True)
        if son_id in ("son_3", "son_4", "son_2"):
            self.sound.play("kovulma")
        elif son_id in ("son_1", "son_6", "son_7", "son_8"):
            self.sound.play("kasa")

        # Kayıtları güncelle (kayit.json)
        self.records["toplam_oyun"] = self.records.get("toplam_oyun", 0) + 1
        yeni_son_acildi = False
        if son_id not in self.records["kesfedilen_sonlar"]:
            self.records["kesfedilen_sonlar"].append(son_id)
            yeni_son_acildi = True
            self.sound.play("yeni_son")

        yeni_rekor = False
        if score > self.records.get("en_yuksek_puan", 0):
            self.records["en_yuksek_puan"] = score
            yeni_rekor = True

        eski_son_puani = self.records.get("son_puanlari", {}).get(son_id, 0)
        if score > eski_son_puani:
            self.records.setdefault("son_puanlari", {})[son_id] = score

        self.save_records()
        self.update_stats()

        # Sonuç Ekranı Mesajları
        toplam_son = len(OYUN_AYARLARI["sonlar"])
        ulasilan_son = len(self.records["kesfedilen_sonlar"])

        baslik_ek = "  [🔓 YENİ SON KEŞFEDİLDİ!]" if yeni_son_acildi else ""
        rekor_ek = "  [🏆 YENİ REKOR!]" if yeni_rekor else ""

        self.say(f"🏁 {son_bilgi['baslik']}{baslik_ek}", son_bilgi["metin"])
        self.say(
            "📊 SONUÇ RAPORU & KOLEKSİYON DURUMU",
            f"• Bu Oyundaki Puanın: {score} / 100{rekor_ek}  (En Yüksek Rekorun: {self.records['en_yuksek_puan']}/100)\n"
            f"• Son Geçmişi: {toplam_son} sondan {ulasilan_son}'ine ulaştın!\n"
            f"• Satıcı Güveni: {trust}/100  |  Memnuniyet: {satisfaction}/100  |  Kalan Bütçe: {tl(self.budget)}"
        )

        self.choice("↻  Yeni Oyun Başlat (Rastgele Satıcı & Cihaz)", self.restart, "primary")
        self.choice(f"🏆  Sonlarım Koleksiyonunu Gör ({ulasilan_son}/{toplam_son} Açık)", self.open_endings_modal, "warning")

    def restart(self):
        self.reset_state()
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self.start_game()

    # ------------------------------------------------------------------------
    # "SONLARIM" KOLEKSİYON PENCERESİ (KİLİTLİ "???" VE REKOR EKRANI)
    # ------------------------------------------------------------------------
    def open_endings_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("🏆 Sonlarım & En Yüksek Puan Geçmişi")
        modal.geometry("680x620")
        modal.minsize(580, 500)
        modal.configure(fg_color="#0b1220")
        modal.transient(self)
        modal.grab_set()

        toplam = len(OYUN_AYARLARI["sonlar"])
        bulunan = len(self.records["kesfedilen_sonlar"])
        rekor = self.records.get("en_yuksek_puan", 0)
        toplam_oyun = self.records.get("toplam_oyun", 0)

        top_frame = ctk.CTkFrame(modal, fg_color="#111c2e", corner_radius=16)
        top_frame.pack(fill="x", padx=18, pady=(16, 10))

        ctk.CTkLabel(
            top_frame,
            text=f"🏆  SON KOLEKSİYONU: {toplam} SONDAN {bulunan}'İNE ULAŞTIN",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#f8fafc"
        ).pack(anchor="w", padx=18, pady=(14, 4))

        ctk.CTkLabel(
            top_frame,
            text=f"🌟 En Yüksek Puan: {rekor} / 100   ·   🎮 Oynanan Oyun: {toplam_oyun}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#fbbf24"
        ).pack(anchor="w", padx=18, pady=(0, 8))

        bar = ctk.CTkProgressBar(top_frame, height=12, corner_radius=6, progress_color="#10b981")
        bar.pack(fill="x", padx=18, pady=(0, 14))
        bar.set(bulunan / max(1, toplam))

        scroll = ctk.CTkScrollableFrame(modal, fg_color="#111c2e", corner_radius=16)
        scroll.pack(fill="both", expand=True, padx=18, pady=(0, 10))

        for s_id, s_data in OYUN_AYARLARI["sonlar"].items():
            unlocked = s_id in self.records["kesfedilen_sonlar"]
            best_for_end = self.records.get("son_puanlari", {}).get(s_id, None)

            card = ctk.CTkFrame(
                scroll,
                fg_color=s_data["renk"] if unlocked else "#162032",
                corner_radius=12,
                border_width=1,
                border_color=s_data["vurgu"] if unlocked else "#25354d"
            )
            card.pack(fill="x", padx=8, pady=5)

            if unlocked:
                puan_etiket = f"  (En İyi Puan: {best_for_end}/100)" if best_for_end is not None else ""
                baslik = f"✅ {s_data['emoji']}  {s_data['baslik']}{puan_etiket}"
                detay = s_data["metin"]
                renk = "#f8fafc"
            else:
                baslik = "🔒  ???  (Kilitli Son)"
                detay = f"İpucu: {s_data['ipucu']}"
                renk = "#94a3b8"

            ctk.CTkLabel(
                card,
                text=baslik,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=renk
            ).pack(anchor="w", padx=14, pady=(10, 2))

            ctk.CTkLabel(
                card,
                text=detay,
                font=ctk.CTkFont(size=12),
                text_color="#cbd5e1" if unlocked else "#64748b",
                wraplength=580,
                justify="left"
            ).pack(anchor="w", padx=14, pady=(0, 10))

        bottom = ctk.CTkFrame(modal, fg_color="transparent")
        bottom.pack(fill="x", padx=18, pady=(0, 14))

        def sifirla():
            self.records = {
                "kesfedilen_sonlar": [],
                "en_yuksek_puan": 0,
                "toplam_oyun": 0,
                "son_puanlari": {}
            }
            self.save_records()
            self.update_stats()
            modal.destroy()
            self.open_endings_modal()

        ctk.CTkButton(
            bottom,
            text="🗑️ Kayıtları Sıfırla",
            command=sifirla,
            fg_color="#7f1d1d",
            hover_color="#991b1b",
            width=140
        ).pack(side="left")

        ctk.CTkButton(
            bottom,
            text="Kapat",
            command=modal.destroy,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            width=120
        ).pack(side="right")

if __name__ == "__main__":
    Game().mainloop()
