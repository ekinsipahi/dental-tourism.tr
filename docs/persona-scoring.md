# Persona motoru — skorlama mantığı (gözlem modu)

**Durum (2026-10-11):** `PERSONA_UI_ENABLED=False`. Motor sayar, teşhis eder, admin'e yazar.
**Arayüz hiç değişmez:** renk, hero, "çok uygun fiyat" çubuğu, canlı mesaj kartı yok; herkes varsayılan sayfayı görür.
Önce gerçek WhatsApp/telefon konuşmalarından niyet etiketlenir. Sistem kanıtlanınca `.env` içinde
`PERSONA_UI_ENABLED=True` ile kişiselleştirme açılır.

## Personalar

| Kod | Admin'de | Ne düşünüyor |
|---|---|---|
| price | 💶 Fiyat | Ne kadar tutar, ödeme |
| quality | 🎯 Kalite / kişiye özel | Doğru tedavi, kişiye özel plan, hekim, uzun ömür |
| premium | 💎 Lüks / VIP | Ayrıcalık, mahremiyet |
| skeptic | 🔍 Şüphe / araştırma | Güvenli mi, yorumlar gerçek mi, tedavileri karşılaştırıyor |
| fear | 😟 Korku / ağrı | Acıtır mı, ters giderse |
| shame | 🙈 Estetik / gülüş | Renk, şekil, önce-sonra |
| urgency | ⚡ Acele / zaman | Kaç gün kalmalıyım, hafta sonu |
| trust | 🤝 Güven / hekim | Dil, hekim deneyimi, videolar |
| ready | ✅ Karar vermiş | İletişim, adres |

## Sinyaller ve puanları

### 1. Sayfa — açılış + okuma süresi (`apps/persona/pages.py`)
- Açılınca sinyalin **%25**'i.
- Çıkarken kalan **%75 × min(süre / 60 sn, 1)**. 5 sn altı = 0.
- Yani 3 sn bakıp çıkan kişi neredeyse hiç puan almaz, 60+ sn okuyan tam puan alır.
- Aynı sayfa türü ziyaret başına en fazla 2 kez sayılır; yenilemek puanı şişirmez.

| Sayfa | Tam puan |
|---|---|
| /prices/, /prices/<tedavi>/ | 💶 1.3 / 1.2 |
| /packages/ | 💶 0.6 + 💎 0.4 |
| "En iyi klinik" rehberleri | 🎯 1.0–1.1 + 🔍 0.5–0.7 |
| Hekim profili / hakkımızda | 🎯 0.9 / 0.5 + 🤝 |
| **Tedavi sayfaları** (implant, lamina, zirkonyum…) | 🔍 0.4–0.5 — *sadece araştırıyor*, tür tercihi sayılmaz |
| Garanti / takip, cerrahi rehberi | 😟 1.0 / 0.9 |
| "Hangi ülke", "Türkiye'de diş yaptırmak" | 🔍 0.7–0.9 |
| Gülüş galerisi | 🙈 1.1 |
| İletişim, İstanbul rehberi | ✅ 1.3 / 0.8 |

### 2. SSS — açtı + kaç saniye okudu (`apps/persona/mindset.py`)
**Ortak SSS:** her sayfanın altında aynı yerde, aynı sorular. Her soru bir personaya **etiketli** (`data-mind-q`):

| Soru | Persona |
|---|---|
| Is it safe…? / Are the reviews and photos real? | 🔍 |
| How much does … cost? | 💶 |
| Does the treatment hurt? | 😟 |
| Will my treatment plan be made for me personally? | 🎯 |
| Can I have a private, discreet appointment? | 💎 |
| Can I choose the shape and shade…? | 🙈 |
| How long do I need to stay? | ⚡ |
| Do you speak my language? / How experienced is the dentist? | 🤝 |

Sayfanın kendi soruları sözlükle sınıflanır:
- "safe / risk" → 🔍 şüphe (korku değil).
- "hurt / painful / acıtır / ağrı / anaesthesia" → 😟 korku.
- "affordable / cost / installment" → 💶 fiyat.

Puan:
- Açınca tam puanın **%30**'u.
- Kapatınca ya da sayfadan çıkınca kalan **%70 × min(okuma sn / 8, 1)**. 2 sn altı = okumadı.
- 1 sn açıp kapatan 0.45, 8+ sn okuyan 1.5 puan alır. Aynı soru ziyaret başına bir kez sayılır.

### 3. Diğer
- **Arama kelimesi (utm_term / Google sorgusu):** cheap → 💶, best/kaliteli → 🎯, luxury/vip → 💎, safe → 😟/🔍.
- **Fiyat notundaki "fiyatımı sor" tıklaması:** 💶 0.8.
- **Sertifika tıklaması:** 😟 1.5. **Önce-sonra etkileşimi:** 🙈 1.2. **Video:** 🤝 0.6.
- **Pasif kutular sayılmaz:** fiyat notu ya da kenar kutusunun ekranda görünmesi puan vermez.

## Karar
- **Olasılık:** puanlar softmax ile olasılığa çevrilir. Kanıt azken "❔ Belirsiz" baskın kalır.
- **Güven seviyesi:**
  - **zayıf:** 2'den az sinyal ya da en yüksek olasılık %45'in altında. Admin'de "Belirsiz (…?)" yazar.
  - **orta:** ikisi arası.
  - **güçlü:** 4+ sinyal ve %65+ olasılık.
- **Yeni ziyaret (30 dk+ ara):** eski kanıt yarıya iner. Bir kez fiyat sayfasına bakan kişi sonsuza dek fiyatçı kalmaz.
- **Aynı cihaz:** `dt_vid` çerezi + localStorage, son teşhis `dt_mind`.

## Admin'de nerede?
- **📞 İletişim tıklamaları:** her arama/WhatsApp/form anında "🧠 Aklındaki" sütunu var.
  - Olasılıklar, güven seviyesi ve "neden?" listesi (hangi sayfada kaç sn, hangi SSS'yi kaç sn okudu).
  - "aklındaki" filtresi ve CSV.
- **Lead'ler:** aynı sütun; lead e-postasında "Aklındaki: …" satırı.
- **Persona → Visitor sessions:** "Şu an aklındaki" + tam **kanıt günlüğü** (zaman, ne yaptı, hangi persona, +puan).
