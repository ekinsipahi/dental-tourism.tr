# Programatik SEO denetimi — Kasım 2026

Soru: "pSEO sayfalarımız spam mi, iyi durumda mı? Aşırı ince içerik var mı, hekim olarak nereleri doldurmalıyım?"

Yöntem: canlı sitemap (1.199 URL) sınıflandırıldı; 15 canlı sayfa `curl` ile, ~45 sayfa yerel SQLite üzerinde `django.test.Client` ile render edildi. Her sayfada `<main>` içindeki görünür metin segmentlere ayrıldı; aynı tipteki kardeş sayfayla **birebir aynı** ve **yalnızca token değişen** (tedavi/semt/ülke adı, rakam) segmentler sayıldı. Kelime sayıları EN sürüm, `<main>` içi (menü + footer hariç). Bu rapor, `docs/expertise-sorulari.md`'deki soruların üzerine kuruludur; oradaki soruları tekrar etmez, referans verir.

---

## A. Net karar

**Kasıtlı spam yok; ama yapısal olarak "doorway / ölçekli şablon içerik" ayak izi büyük.** Gizli metin, keyword yığma, sahte aciliyet, sahte fiyat yok; başlıklar benzersiz, fallback diller ve tedavi×şehir sayfaları doğru şekilde `noindex`, canonical/hreflang/x-default düzgün, hekim kutusu + gerçek fotoğraf + yorum her sayfada var. **Buna karşılık indekslenen ~1.080 detay URL'sinin yaklaşık %55'inde (semt 221 + ülke 38 + fiyat 160 + paket 160) sayfaya özgü içerik %25'in altında; semt ve ülke sayfalarında %5'in altında.** Google'ın "doorway pages" ve "scaled content abuse" tanımları tam olarak bu kalıbı hedefler: aynı kliniğe çıkan, token değiştiren yüzlerce sayfa × 17 dil. Şu an ceza işareti olmasa da büyüme ve dayanıklılık riski yüksek; çözüm teknik değil, **içerik + budama**.

### Ölçüm tablosu (EN, `<main>` içi)

| Sayfa tipi | Canlı URL (17 dil) | Örnek çift | Kelime | Sayfaya özgü | Robots | Risk |
|---|---|---|---|---|---|---|
| Semt `/dental-clinic/<semt>/` | 221 | taksim ↔ nisantasi ↔ maslak | ~1.500 | **%0,9–3,9** (13–58 kelime) | index, 17 dilde | **Yüksek** |
| Ülke `/dental-holidays-from/<ülke>/` | 38 | united-kingdom ↔ united-states ↔ ireland | ~1.440 | **%0,6–4,6** (9–67 kelime) | index | **Yüksek** |
| Fiyat `/prices/<tedavi>/` | 160 | teeth-cleaning ↔ composite-veneers ↔ dental-implants | 1.380–1.760 | %1,4–23 (özgü kısım = tedavi SSS'si, o da tedavi ve paket sayfasında aynen var) | index | **Yüksek** (küçük tedaviler) / Orta |
| Paket `/packages/<tedavi>/` | 160 | aynı üçlü | 1.500–1.800 | %10–24 | index | Orta-yüksek |
| Tedavi `/treatments/<tedavi>/` | 160 | dental-implants ↔ composite-veneers ↔ teeth-cleaning | 720–1.280 (**gövde 31–185**) | %10–50 | index | Orta (ince) |
| Rehber `/guide/<konu>/` | 242 | dental-tourism ↔ ankara ↔ guarantee | 1.380–1.670 (**gövde 67–254**) | %10–23 | index | Orta |
| Tedavi×şehir | 10 (sitemap dışı) | /treatments/dental-implants/istanbul/ | 1.560 | — | noindex | Düşük (gereksiz) |
| Hekim `/dentists/…` | 2×16 | ekin-sipahi | 600–740 (**bio 48 / 169 kelime**) | — | index | E-E-A-T zayıf |

Tipler arası: aynı tedavinin `/prices/X` ↔ `/packages/X` sayfaları **%9,6** özgü; `/treatments/X` ↔ `/packages/X` %18,8. Yani bir tedavi için 3 sayfa × 17 dil = 51 URL, pratikte aynı sayfa.

Her pSEO sayfasında `<main>` içindeki ortak blok yaklaşık **1.250–1.380 kelime**: hero "hook" cümlesi, hekim kutusu + 3 adım + "Healthy enamel never grows back" (`templates/pseo/_proof.html`), aynı 3 yorum (`apps/seo/common.py:127-150`), galeri + video (`_photos.html`), önce-sonra, fiyat notu (`_price_note.html`), güven linkleri (`_links.html`), CTA ve **9 ortak SSS** (`apps/core/templatetags/site_tags.py:186-229`, her sayfaya `faq_block` ile eklenir, :240-268). Üstüne menü 125 + footer 67 link.

Ne iyi durumda: tüm başlıklar benzersiz (token şablonu olsa da), `name="keywords"` yok, `package_data.keywords_for` / `area_data.keywords_for` listeleri **hiçbir şablonda render edilmiyor** (canlı HTML'de 0 eşleşme) — yalnızca dokümantasyon; `.sr-only` sadece erişilebilirlik için; anahtar kelime yoğunluğu normal (tedavi adı 10–13/1.800 kelime ≈ %0,7; "WhatsApp" 19–20/sayfa — CTA ağırlığı yüksek ama stuffing değil).

---

## B. Riskler (önem sırasıyla)

1. **Semt sayfaları = doorway kalıbı.** 13 semt × 17 dil = 221 indeksli URL, hepsi aynı kliniğe; sayfaya özgü içerik yalnızca metro satırı, "about 3.5 km", taksi bandı ve 3–4 yer adı (`apps/seo/area_views.py:82-99`, `_faq` :62-75; `templates/areas/detail.html:8-17`). Danca/Azerice/Bulgarca "Tannlege Maslak" gibi ~150 sayfanın arama talebi yok (`area_views.py:17` LANGS = tüm diller; `apps/core/sitemaps.py:227-240`).
2. **Ülke sayfaları = doorway kalıbı.** 33 ülke (`apps/seo/package_data.py:17-51`), her birinde değişen tek veri uçuş saati + kalkış şehirleri + (uzun yol ise) 1 cümle (`templates/packages/origin.html:16-18`; SSS `package_views.py:170-189`). Veritabanında ülkeye özgü yorum yok (yorumlar: TR 14, RU 1, NL 1) → "Patients from X" bölümü hiçbir ülke sayfasında çıkmıyor.
3. **Fiyat/paket sayfalarında küçük tedaviler.** "Teeth Cleaning package in Istanbul", "Tooth Fillings cost in Turkey — fixed quote" (`apps/seo/views.py:136-138`, `package_views.py:98`) — turist için anlamsız, %1,4 özgü. Paket sayfasındaki "How to choose the best Teeth Cleaning clinic in Istanbul" paragrafı (`templates/packages/treatment.html:20-27`) her tedavide aynı; fiyat sayfasındaki "What affects the price / Included in your quote" listeleri (`templates/seo/treatment_price.html:9-22`) tedaviden bağımsız 8 madde.
4. **Üç sayfa tipinde aynı SSS + aynı FAQPage schema.** Tedavi SSS'si (`t_loc.faq`) tedavi, fiyat ve paket sayfasında JSON-LD olarak tekrarlanıyor (`views.py:134`, `package_views.py:96`). Ortak 9 SSS ise görünür metin olarak 1.199 sayfada.
5. **İnce kaynak içerik.** Tedavi gövdeleri 31–185 kelime (3 tedavi 31–33 kelime: temizlik, dolgu, beyazlatma); rehber gövdeleri 67–254 kelime (`apps/seo/topics.py`). Hekim profili: Dt. Ekin bio 48 kelime, mezuniyet yılı/okul boş (`apps/clinics/models.py:368-371`).
6. **Doğrulanmamış kanıt sinyalleri.** `proof()` DB boşsa "4.9" ve 100 döndürür (`apps/core/seo.py:239-248`); DB'deki yorum sayısı da tam 100 — gerçek mi, varsayılan mı doğrulanmalı. Schema'da `openingHours: Mo-Su 05:00-23:59` (klinik kaydı) ve her sayfada "open 7 days" iddiası; klinik meta açıklamasında "10,000+". Başlıklarda "★4.9" (semt sayfaları, `area_views.py:85,92`) — Google yıldız karakterini önermiyor, yeniden yazabilir.
7. **Çeviri pürüzleri (DE/RU).** Gövde çevirileri iyi; UI dizgelerinde cinsiyet/çekim hataları ve karışık dil (bkz. §E).

---

## C. Doldurulacak yerler — hekim için harita

Kural aynı: Türkçe, birinci ağızdan, 3–6 cümle, rakam/marka/gerçek gözlem; fiyat yok. Önce **1 → 2 → 3** sırasıyla. `expertise-sorulari.md`'deki kodlar (A1–A10, B1–B3, C1–C2, D1, E1–E2) olduğu gibi geçerli; aşağıda yalnızca **eksik olanlar** ve **hangi slota gideceği** var.

### 1. Tedavi + fiyat + paket üçlüsü (etki en yüksek: 480 URL)

Slotlar: tedavi gövdesi (`Treatment.body`, admin); paket sayfası için hazır ama **boş** `LandingPage(treatment_price).intro/body/faq` (10 kayıt, `apps/seo/models.py:87-132`, şablonda `templates/packages/treatment.html:9,28`); fiyat sayfasında yeni bir "Hekimin notu" bloğu gerekiyor (slot yok, eklenmeli).

- **Her tedavi için fiyat sayfasına** (A-sorularına ek): "Bu tedavide fiyatı asıl belirleyen 3 şey nedir ve hangi muayene bulgusu teklifi değiştirir?" (implant: kemik grefti/sinüs lift, abutment tipi, anında/geç yükleme; lamina: diş sayısı, mock-up, e.max vs feldspatik; kanal: kanal sayısı, retreatment). Bu cevap `treatment_price.html:9-15`'teki genel 4 maddenin **yerine** geçmeli.
- **Her tedavi için paket sayfasına**: "Yurt dışından gelen hasta için bu tedavinin gün gün programı nedir; iki geliş arasında ne yaşanır; tek gelişe sığmayan durum hangisi?" (C1'in tedaviye özel hâli → `LandingPage.body`).
- **Reddettiğiniz vakalar**: "Bu tedaviyi hangi hastaya yapmayı reddediyorsunuz ve ne öneriyorsunuz?" (kompozit lamina, Hollywood smile, beyazlatma, zirkonyum için ayrı ayrı; A3-2 ve A8-3 kısmen var, diğerleri yok).
- **Malzeme**: `ClinicTreatment.brands` ve `warranty_years` alanları (`apps/clinics/models.py:436-437`) tüm tedavilerde boş ve sayfada gösterilmiyor. Marka + garanti yılını yazın; "Materials we use" satırı olarak üç sayfaya da eklenmeli (teknik iş).
- **KALDIR / BİRLEŞTİR**: temizlik, dolgu, beyazlatma için `/prices/` ve `/packages/` sayfaları (6 × 17 = 102 URL) — içerik gelmeden `noindex` veya tedavi sayfasına 301. Paket şablonundaki "How to choose the best X clinic" paragrafı (`packages/treatment.html:20-27`) tüm tedavilerde kaldırılmalı; yerine hekim notu.

### 2. Ülke sayfaları (38 URL) — doldur **veya** buda

Slot yok; `ORIGINS` sözlüğüne ülke başına `note` alanı (veya admin modeli) eklenmeli. C2'ye ek, **yalnızca gerçekten hasta gelen ülkeler** için:

- "Bu ülkeden gelen hastalar en çok hangi tedavi için geliyor ve evdeki diş hekimleriyle nasıl bir sorun yaşamış oluyorlar?" (İngiltere: NHS bekleme/fiyat; Almanya: Heil- und Kostenplan, Krankenkasse geri ödeme sorusu; Hollanda: sigorta; Körfez: yoğun program/mahremiyet.)
- "Evdeki hekimden hangi belgeyi istiyorsunuz (OPG/CBCT formatı, raporlar) ve dönüşte kontrolü evdeki hekimle nasıl paylaşıyorsunuz?"
- "Bu ülkeden bir hastanın tedavisini anlatın (anonim): kaç geliş, ne yapıldı, dönüşte ne oldu?"
- **KALDIR**: yorumu ve hekim notu olmayan ülkeler (KW, BH, OM, QA, MD, BY, KZ, NZ vb.) `noindex,follow` kalsın; menüde dursun, sitemap'ten çıksın.

### 3. Semt sayfaları (221 URL) — önce buda, sonra doldur

- **BİRLEŞTİR**: Şişli (klinik burada) kalsın; "near" sayfaları 3 kümeye indir (Nişantaşı/Osmanbey/Mecidiyeköy, Taksim/Beşiktaş/Ortaköy, Levent/4.Levent/Etiler/Maslak/Gayrettepe/Kağıthane) veya 13 sayfayı yalnızca hub'a bağlayıp detayları `noindex` yap. Dilleri İstanbul'da yaşayan/konaklayan kitlenin dilleriyle sınırla (en, tr, ar, ru, de): 221 → ~20–25 URL.
- D1'e ek (kalan sayfalar için): "Bu semtten gelen hastalarınızda ne fark ediyorsunuz? (Nişantaşı: estetik talebi; Levent/Maslak: plaza çalışanı, öğle arası; Taksim: turist/acil ağrı)" ve "Semtteki otel/konaklama misafiri için acil randevu nasıl işliyor, aynı gün çekim/kanal yapıyor musunuz?"
- `_faq` (:62-75) "How do I get here from X" 4 sorusu token-swap; kalan sayfalarda 2 soruya indirilip hekim notu eklenmeli.

### 4. Rehberler (242 URL)

Slot: `SeoTopic.body` (admin). E1–E2'ye ek:

- `teeth-done-in-turkey` (199 kelime): "Başka klinikte yapılmış işi düzeltmek için gelen 3 hasta: ne yanlış gitmişti, ne yaptınız?" (E2-2'yi somutlar).
- `best-dental-clinic-istanbul` / `best-dental-clinic-turkey`: "Kendi aileniz başka bir kliniğe gidecek olsa soracağınız 5 soru ve 'bu cevabı alırsanız gitmeyin' kriteri."
- `dental-surgery-turkey` (98): "Hangi cerrahileri kendiniz yapıyorsunuz, hangilerini sevk ediyorsunuz (20 yaş dişi, sinüs lift, greft)? Sevk ettiğinizde hasta programı nasıl etkileniyor?"
- `smile-gallery` (91): 6 vakanın her biri için 2 cümle: "Tanı neydi, kaç dişe dokunuldu, neyi yapmayı **reddettiniz**?" (`BeforeAfterCase.caption`).
- `dental-guarantee-aftercare` (92): E1 + "Garanti dışı kalan gerçek bir durum ve nasıl çözdünüz?"
- `istanbul-guide` (163): ekipten pratik bilgi: "Cerrahi sonrası ne yesin, hangi eczane, otel seçiminde neye dikkat?" (hekim değil, asistan yazabilir.)
- **KALDIR / BİRLEŞTİR**: `dental-clinic-ankara` (67 kelime), `dental-care-antalya`, `dental-clinic-aegean` → tek "Türkiye'nin başka şehrinden / tatil bölgesinden gelen hastalar" sayfası.

### 5. Hekim kutusu ve profiller (her sayfada görünür)

B1–B3 geçerli. Ek: Dt. Ekin için mezuniyet yılı, okul, üyelikler alanlarını doldurun (`Doctor.graduation_year/university/memberships`); `_proof.html:10-12` sabit 3 maddenin yerini bu alanlar almalı. Dr. Devrim için diploma/oda kaydı ve kaç yıldır bu adreste olduğunuz; "Ağız-diş-çene radyolojisi" eğitiminin somut bir vaka ile anlatımı (B1-1) özellikle E-E-A-T için.

### 6. Kaldırılması / seyreltilmesi gerekenler (doldurmak yerine)

- Ortak 9 SSS'nin pSEO sayfalarında gösterimi (`site_tags.py:240-268`): ana sayfa + hakkımızda'da kalsın; pSEO'da en fazla 2 (fiyat, güven).
- "Dental work is more than a Hollywood smile" bir sayfada 2–3 kez + footer (`_hero.html:8`, `origin.html:19`, `treatment_price.html:23`, footer:6): tek yerde kalsın.
- Tedavi sayfasındaki "X by city" çipleri (`templates/treatments/detail.html:29-32`) `noindex` tedavi×şehir sayfalarına gidiyor; 20 `LandingPage(treatment_city)` kaydıyla birlikte kaldırılabilir.

---

## D. Hızlı teknik düzeltmeler (uygulanmadı, tarif)

1. **Koşullu indeks**: fiyat ve paket sayfaları yalnızca hekim notu (`LandingPage.body`) doluysa `index`; aksi hâlde `noindex,follow` (`apps/seo/views.py:139-141`, `package_views.py:100-102`). Ülke sayfaları yalnızca `note` veya o ülkeden ≥1 yorum varsa `index`. Sitemap sınıfları aynı koşulu kullanmalı (`sitemaps.py:196-224`).
2. **Semt dilleri**: `area_views.py:17` ve `AreaSitemap` için dil listesi `{en,tr,ar,ru,de}`; kalan dillerde `noindex` + hreflang kümesinden çıkar.
3. **x-default**: 32 ülke sayfasında (EN sürümü olmayan: `/de/zahnurlaub-aus/deutschland/` …) x-default yok (`apps/core/seo.py:86-88` yalnızca EN'i alır). O dilin kendi URL'sini x-default yap.
4. **SSS tekilleştirme**: tedavi SSS'si yalnızca tedavi sayfasında; fiyat/paket kendi `LandingPage.faq` slotunu kullanmalı; `core_faq` pSEO'dan çıkarılmalı.
5. **Başlıklar**: "★4.9" karakterini title'dan çıkar (`area_views.py:85,92,117`); "2026" sabit metin (`topics.py` meta_title'ları, gettext dizgeleri) — yıl dinamik olmalı, Ocak'ta bayatlar. Fiyat/paket meta açıklamaları token şablonu (`views.py:137`, `package_views.py:99`) → `LandingPage.meta_description` doldurulunca onu kullan.
6. **Kanıt verileri**: `proof()` varsayılanlarını (4.9 / 100) kaldır, DB boşsa yıldız gösterme; `google_review_count` gerçek değerle güncelle; `opening_hours` gerçek saat; "10,000+" iddiasını kaynaklandır veya sil.
7. **Çeviri dizgeleri**: "Graduate of Ankara University…" → kadın hekim için "Absolventin" / "Выпускница" (`_proof.html:10`, .po); "Translated from {{ l }}" (`components/reviews.html:30`) dil adını hedef dilde ver ("Türkçe" → "Türkisch"/"турецкого"); km değerleri `f"{x:g}"` (`area_views.py:21`) yerine yerel ondalık (DE "3,5 km"); RU'da tedavi adı yalın hâlde cümleye giriyor ("От чего зависит цена (Зубные импланты)", "Всё о процедуре: Зубные импланты") — iki nokta/parantez yerine çekimsiz kalıp; DE "Professionelle Zahnreinigung-Paket" → "Paket: Professionelle Zahnreinigung".
8. **Dış link tekrarı**: drdevrim.com / devrimbirikensipahi.com.tr her sayfada 2 kez (footer:25-26 + `_links.html`); biri yeter. wa.me 14×/sayfa normal (CTA), ama `_price_note` + sidebar + hero + footer aynı metinle — tasarım sadeleşmesi.

---

## E. Çeviri spot kontrolü (DE / RU)

Gövde çevirileri (tedavi, rehber) akıcı ve doğru terimli; yerel okur için makine izi az. Sorunlar UI dizgelerinde: **DE** — "Absolvent der Zahnmedizinischen Fakultät" (kadın hekim), "Übersetzt aus dem Türkçe", "etwa 3.5 km", "Professionelle Zahnreinigung-Paket", "Ich empfehle sie blind" (gözüm kapalı'nın birebir çevirisi; "ohne Vorbehalt"). **RU** — "Выпускник…" (kadın), "Переведено с языка: Türkçe", "От чего зависит цена (Зубные импланты)", "Рекомендую с закрытыми глазами" (birebir). Tüm çeviri kayıtları `status=reviewed` ama `model_used=seed_*` — yani seed dosyasından geldi, insan incelemesi yapılmamış olabilir; DE/RU için en az hekim kutusu + SSS dizgelerinin bir anadil konuşuru tarafından okunması önerilir.

---

## Özet

Site "spam sitesi" değil; dürüst ton, gerçek fotoğraf/yorum ve temiz indeks hijyeni var. Sorun, **1.199 URL'nin büyük kısmının aynı ~1.300 kelimelik şablonu taşıması ve sayfaya özgü kısmın 10–60 kelimeye düşmesi**. Öncelik: (1) tedavi/fiyat/paket üçlüsüne hekim notu + küçük tedavilerin fiyat/paket sayfalarını kapatmak, (2) semt sayfalarını ~20'ye, ülke sayfalarını gerçek pazarlara indirmek, (3) ortak SSS ve tekrarlanan sloganları seyreltmek, (4) kanıt verilerini (yorum sayısı, çalışma saati) doğrulamak. Bunlar yapıldığında kalan ~400–500 URL, hekim içeriğiyle gerçek bir uzmanlık sitesine dönüşür.
