def start_game(self):
        # Oyun artık doğrudan başlamak yerine selamlaşma aşamasıyla açılır
        self.scene.configure(text="Mağazaya Giriş")
        self.say("Oyun Başladı", "Mağazanın kapısından içeri adımını attın. Satıcı Hasan Abi tezgahın arkasında oturuyor.")
        self.show_greeting_choices()

    def show_greeting_choices(self):
        self.clear_choices()
        self.choice("👋 'Selamünaleyküm ustam, kolay gelsin!' diyerek sıcak bir selam ver.", lambda: self.handle_greeting("saygili"))
        self.choice("🤝 'Merhaba, iyi günler. Kolay gelsin.' de.", lambda: self.handle_greeting("normal"))
        self.choice("💬 (Selam vermeden) 'Direkt şu 8.500 TL'lik telefona bakacaktım, son fiyatı nedir?' de.", lambda: self.handle_greeting("kaba"))

    def handle_greeting(self, attitude):
        if attitude == "saygili":
            self.trust = min(100, self.trust + 15)
            self.satisfaction = min(100, self.satisfaction + 5)
            self.say("Sen · Alıcı", "Selamünaleyküm ustam, kolay gelsin! Hayırlı işler.")
            self.say("Satıcı Hasan Abi", "Aleykümselam delikanlı, hoş geldin! Çok teşekkür ederim, buyur nasıl yardımcı olayım?")
            self.say("Oyun notu", "Esnafa saygılı ve sıcak davrandın. Güven ve memnuniyet puanın büyük ölçüde arttı! (+15 Güven)")
        elif attitude == "normal":
            self.trust = min(100, self.trust + 5)
            self.say("Sen · Alıcı", "Merhaba, iyi günler. Kolay gelsin.")
            self.say("Satıcı Hasan Abi", "Merhaba, hoş geldiniz. Teşekkürler, buyurun neye bakmıştınız?")
            self.say("Oyun notu", "Doğal ve kibar bir giriş yaptın. (+5 Güven)")
        else:
            self.trust = max(0, self.trust - 15)
            self.satisfaction = max(0, self.satisfaction - 5)
            self.say("Sen · Alıcı", "Selam. Direkt şu 8.500 TL'lik telefona bakacaktım, en son kaça olur bu?")
            self.say("Satıcı Hasan Abi", "(Hafifçe şaşırarak ve mesafeli bir tavırla) Hoş geldin. Valla cihazın fiyatı yazıyor orada, temiz telefon, çok bir şey yapamam...")
            self.say("Oyun notu", "Selam vermeden doğrudan fiyata girmek esnafın hoşuna gitmedi. Pazarlık şansını zora soktun! (-15 Güven)")

        self.update_stats()
        # Selamlaşmadan sonra ana seçimleri göster
        self.clear_choices()
        self.choice("Devam et", self.show_main_choices)