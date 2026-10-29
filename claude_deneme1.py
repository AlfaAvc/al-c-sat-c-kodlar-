"""PAZARLIK ZAMANI - İkinci El Telefon
Kurulum: python -m pip install customtkinter
Çalıştırma: python main.py
"""
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

PRICE = 8500
START_BUDGET = 8000


def tl(amount):
    """8500 -> '8.500 TL'"""
    return f"{amount:,}".replace(",", ".") + " TL"


class Game(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pazarlık Zamanı | İkinci El Telefon")
        self.geometry("1050x720")
        self.minsize(850, 620)
        self.configure(fg_color="#0b1220")
        self.reset_state()
        self.build_ui()
        self.update_stats()  # DÜZELTME: açılışta doğru bütçe görünsün
        self.start_game()

    def reset_state(self):
        self.budget = START_BUDGET
        self.trust = 50
        self.satisfaction = 50
        self.inspected = False
        self.offer = None
        self.purchased = False
        self.finished = False
        self.last_price = PRICE

    def current_price(self):
        """Pazarlık yapıldıysa son fiyat, yapılmadıysa etiket fiyatı."""
        return self.last_price if self.offer is not None else PRICE

    def build_ui(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="#111c2e", corner_radius=18)
        header.grid(row=0, column=0, columnspan=2, padx=18, pady=(18, 12), sticky="ew")
        ctk.CTkLabel(header, text="📱  PAZARLIK ZAMANI", font=ctk.CTkFont(size=25, weight="bold"), text_color="#f3f7ff").pack(anchor="w", padx=22, pady=(15, 2))
        ctk.CTkLabel(header, text="İkinci el telefon mağazası · Kararlarını ver, sonucu sen belirle.", font=ctk.CTkFont(size=13), text_color="#9fb0c8").pack(anchor="w", padx=23, pady=(0, 15))

        left = ctk.CTkFrame(self, fg_color="#111c2e", corner_radius=18)
        left.grid(row=1, column=0, padx=(18, 9), pady=(0, 18), sticky="nsew")
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(left, text="MAĞAZA DİYALOĞU", font=ctk.CTkFont(size=12, weight="bold"), text_color="#8da4c4").grid(row=0, column=0, padx=20, pady=(18, 8), sticky="w")
        self.scene = ctk.CTkLabel(left, text="Mağazaya hoş geldin", font=ctk.CTkFont(size=20, weight="bold"))
        self.scene.grid(row=1, column=0, padx=20, pady=(0, 8), sticky="w")
        self.log = ctk.CTkTextbox(left, wrap="word", corner_radius=12, fg_color="#0b1424", text_color="#e4ebf5", font=ctk.CTkFont(size=14), border_width=1, border_color="#25354d")
        self.log.grid(row=2, column=0, padx=18, pady=8, sticky="nsew")
        self.log.configure(state="disabled")
        self.choices = ctk.CTkFrame(left, fg_color="transparent")
        self.choices.grid(row=3, column=0, padx=18, pady=(8, 18), sticky="ew")
        self.choices.grid_columnconfigure(0, weight=1)

        right = ctk.CTkFrame(self, fg_color="#111c2e", corner_radius=18)
        right.grid(row=1, column=1, padx=(9, 18), pady=(0, 18), sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(right, text="ALIŞVERİŞ ÖZETİ", font=ctk.CTkFont(size=12, weight="bold"), text_color="#8da4c4").grid(row=0, column=0, padx=18, pady=(18, 12), sticky="w")
        product = ctk.CTkFrame(right, fg_color="#1b2a40", corner_radius=14)
        product.grid(row=1, column=0, padx=15, pady=(0, 12), sticky="ew")
        ctk.CTkLabel(product, text="📱  İkinci el akıllı telefon", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=15, pady=(14, 4))
        ctk.CTkLabel(product, text="Durum: İyi · Pil: %84 · Kutu mevcut", font=ctk.CTkFont(size=12), text_color="#b9c8dc").pack(anchor="w", padx=15, pady=(0, 5))
        ctk.CTkLabel(product, text=f"Etiket fiyatı: {tl(PRICE)}", font=ctk.CTkFont(size=14), text_color="#b9c8dc").pack(anchor="w", padx=15, pady=(0, 14))
        self.budget_label = self.stat(right, 2, "Kalan bütçe", tl(START_BUDGET))
        self.trust_label = self.stat(right, 3, "Satıcının güveni", "50 / 100")
        self.satisfaction_label = self.stat(right, 4, "Memnuniyet", "50 / 100")
        ctk.CTkLabel(right, text="OYUN HEDEFİ", font=ctk.CTkFont(size=12, weight="bold"), text_color="#8da4c4").grid(row=5, column=0, padx=18, pady=(16, 6), sticky="w")
        ctk.CTkLabel(right, text="Telefonu bilinçli değerlendir,\nbütçeni koru ve iyi bir anlaşma yap.", justify="left", text_color="#cbd5e1").grid(row=6, column=0, padx=18, pady=(0, 14), sticky="w")
        ctk.CTkButton(right, text="↻  Oyunu yeniden başlat", command=self.restart, fg_color="#26364d", hover_color="#344964").grid(row=7, column=0, padx=16, pady=(0, 16), sticky="ew")

    def stat(self, parent, row, title, value):
        card = ctk.CTkFrame(parent, fg_color="#172439", corner_radius=12)
        card.grid(row=row, column=0, padx=15, pady=5, sticky="ew")
        ctk.CTkLabel(card, text=title, text_color="#9fb0c8", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=12, pady=(9, 0))
        label = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=18, weight="bold"))
        label.pack(anchor="w", padx=12, pady=(0, 9))
        return label

    def say(self, who, text):
        self.log.configure(state="normal")
        self.log.insert("end", f"{who}\n{text}\n\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def clear_choices(self):
        for child in self.choices.winfo_children():
            child.destroy()

    def choice(self, text, command, secondary=False):
        ctk.CTkButton(self.choices, text=text, command=command, height=40, anchor="w", corner_radius=10,
                      fg_color="#26364d" if secondary else "#2563eb",
                      hover_color="#344964" if secondary else "#1d4ed8").pack(fill="x", pady=4)

    def update_stats(self):
        self.budget_label.configure(text=tl(self.budget))
        self.trust_label.configure(text=f"{max(0, min(100, self.trust))} / 100")
        self.satisfaction_label.configure(text=f"{max(0, min(100, self.satisfaction))} / 100")

    def start_game(self):
        self.say("Satıcı", f"Merhaba! Bu telefonun fiyatı {tl(PRICE)}. Cihaz temiz kullanıldı.")
        self.say("Sen · Alıcı", "Merhaba. Telefonla ilgileniyorum ama önce birkaç şey öğrenmek istiyorum.")
        self.show_main_choices()

    def show_main_choices(self):
        self.clear_choices()
        self.choice("🔎  Telefonu ve pil durumunu incele", self.inspect)
        self.choice("🤝  Fiyat için pazarlık yap", self.bargain)
        self.choice("💳  İncelemeden satın almayı kabul et", self.buy_blind, True)
        self.choice("🚪  Teşekkür edip mağazadan ayrıl", self.leave, True)

    def inspect(self):
        if self.finished:
            return
        self.say("Sen · Alıcı", "Pil sağlığını, ekranı ve cihazın geçmişini kontrol edebilir miyim?")
        if not self.inspected:
            # DÜZELTME: puan sadece ilk incelemede artar
            self.inspected = True
            self.trust = min(100, self.trust + 12)
            self.satisfaction = min(100, self.satisfaction + 8)
            self.say("Satıcı", "Tabii. Pil sağlığı %84. Ekranda belirgin çatlak yok; ancak kasanın kenarında küçük bir çizik var.")
            self.say("Oyun notu", "Ürünü inceleyerek daha bilinçli karar verdin. Güven ve memnuniyet puanın arttı.")
        else:
            self.say("Satıcı", "Az önce birlikte baktık, yeni bir şey çıkmadı. Pil %84, kasada küçük bir çizik var.")
        self.update_stats()
        self.clear_choices()
        self.choice("Şimdi pazarlık yap", self.bargain)
        self.choice(f"{tl(self.current_price())} fiyatla satın almayı değerlendir", self.purchase_options, True)
        self.choice("Bu ürün bana uygun değil, ayrıl", self.leave, True)

    def bargain(self):
        if self.finished:
            return
        self.scene.configure(text="Fiyat pazarlığı")
        self.say("Sen · Alıcı", "Bütçemi aşmak istemiyorum. Bir indirim yapabilir misiniz?")
        self.clear_choices()
        self.choice("7.000 TL teklif et", lambda: self.make_offer(7000))
        self.choice("7.800 TL teklif et", lambda: self.make_offer(7800))
        self.choice("İndirim istemeden devam et", self.purchase_options, True)
        self.choice("Pazarlığı bırak ve ayrıl", self.leave, True)

    def make_offer(self, amount):
        if self.finished:
            return
        first = self.offer is None  # DÜZELTME: puan etkisi sadece ilk teklifte
        self.offer = amount
        self.say("Sen · Alıcı", f"{tl(amount)} teklif ediyorum.")
        if amount == 7800:
            if first:
                self.trust = min(100, self.trust + 8)
                self.satisfaction = min(100, self.satisfaction + 8)
            self.last_price = 8000
            self.say("Satıcı", "Biraz daha çıkabilirsem size yardımcı olabilirim. 8.000 TL son fiyatım olsun.")
        else:
            if first:
                self.trust = max(0, self.trust - 5)
                self.satisfaction = max(0, self.satisfaction - 2)
            # DÜZELTME: çok düşük teklif artık farklı sonuç verir
            self.last_price = 8200
            self.say("Satıcı", "Bu fiyat benim için çok düşük kaldı. En fazla 8.200 TL'ye inebilirim.")
        self.update_stats()
        self.clear_choices()
        self.choice(f"{tl(self.last_price)} karşı teklifi kabul et", lambda: self.complete_purchase(self.last_price))
        self.choice("Yeni bir teklif ver", self.bargain, True)
        self.choice("Bir kez daha düşün ve ürünü incele", self.inspect, True)
        self.choice("Anlaşamadık, ayrıl", self.leave, True)

    def purchase_options(self):
        if self.finished:
            return
        self.clear_choices()
        price = self.current_price()
        self.say("Satıcı", f"Son fiyatımız {tl(price)}.")
        if price <= self.budget:
            self.choice(f"{tl(price)}'ye satın al", lambda: self.complete_purchase(price))
        else:
            self.choice(f"Bütçemi aşarak {tl(price)}'ye satın al", lambda: self.complete_purchase(price))
        self.choice("Bir kez daha pazarlık yap", self.bargain, True)
        self.choice("Vazgeç ve ayrıl", self.leave, True)

    def buy_blind(self):
        if self.finished:
            return
        # DÜZELTME: pazarlık yapıldıysa son fiyat geçerli
        price = self.current_price()
        self.say("Sen · Alıcı", "Telefonu fazla incelemeden alacağım.")
        self.say("Satıcı", "Elbette. Ödeme işlemini yapabiliriz.")
        self.satisfaction -= 8
        self.complete_purchase(price)

    def complete_purchase(self, price):
        if self.finished:
            return
        overspend = price > self.budget
        self.purchased = True
        self.budget -= price
        if overspend:
            self.satisfaction -= 20
            self.say("Sen · Alıcı", "Bütçemi aşmayı kabul ediyorum.")
        else:
            self.satisfaction = min(100, self.satisfaction + 12)
        self.say("Satıcı", "Teşekkür ederim! Güle güle kullanın.")
        self.update_stats()
        self.finish()

    def leave(self):
        if self.finished:
            return
        self.say("Sen · Alıcı", "Teşekkür ederim, şimdilik satın almaktan vazgeçiyorum.")
        self.say("Satıcı", "Elbette. Fikriniz değişirse yine bekleriz.")
        self.finish()

    def finish(self):
        self.finished = True
        self.clear_choices()
        trust = max(0, min(100, self.trust))
        satisfaction = max(0, min(100, self.satisfaction))
        bargained = self.offer is not None and self.last_price < PRICE
        if not self.purchased:
            ending = "SON 4 — ALIŞVERİŞ TAMAMLANMADI"
            detail = "Anlaşma sağlanmadı veya ürünü almaktan vazgeçtin. Bütçeni korudun."
        elif self.budget < 0 or satisfaction < 35:
            ending = "SON 5 — PİŞMANLIK"
            detail = "Bütçeni aştın veya yeterince memnun kalmadın. Daha dikkatli değerlendirebilirdin."
        elif self.inspected and bargained and trust >= 70:
            ending = "SON 3 — BİLİNÇLİ ALIŞVERİŞ"
            detail = "Telefonu inceledin, pazarlık yaptın ve bütçene uygun, güvenli bir anlaşma yaptın."
        elif bargained:
            ending = "SON 2 — BAŞARILI PAZARLIK"
            detail = "Pazarlık yaparak fiyatı düşürdün ve alıcı olarak avantaj sağladın."
        else:
            ending = "SON 1 — ACELE ALIŞVERİŞ"
            detail = "Ne pazarlık yaptın ne de ürünü inceledin. Bu sefer sorun çıkmadı ama risk aldın."
        score = max(0, min(100, round((trust + satisfaction + (50 if self.budget >= 0 else 0)) / 2.5)))
        self.scene.configure(text="Alışveriş tamamlandı")
        self.say("🏁 " + ending, detail)
        self.say("SONUÇ RAPORU", f"Toplam puan: {score}/100\nSatıcı güveni: {trust}/100\nMemnuniyet: {satisfaction}/100\nKalan bütçe: {tl(self.budget)}")
        self.choice("↻  Yeniden oyna", self.restart)

    def restart(self):
        self.reset_state()
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self.scene.configure(text="Mağazaya hoş geldin")
        self.update_stats()
        self.start_game()


if __name__ == "__main__":
    Game().mainloop()