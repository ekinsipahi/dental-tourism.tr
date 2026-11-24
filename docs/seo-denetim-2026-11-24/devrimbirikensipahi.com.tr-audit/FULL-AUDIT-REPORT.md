# devrimbirikensipahi.com.tr — SEO Denetim Raporu (24.11.2026)

Araç: claude-seo v2.6.2 (yalnızca ücretsiz araçlar; PageSpeed API anahtarı ve Chromium olmadan laboratuvar CWV verisi alınamadı). Tarama: sitemap, robots, 10–13 canlı sayfa, JSON-LD, hreflang, güvenlik başlıkları, sunucu süresi. Rapor hekim için Türkçe. Ham veri: data/.

## 1. Yönetici özeti

**SEO Sağlık Skoru: 57/100**  ·  İş tipi: Kurumsal klinik sitesi + blog (yerel, marka); Django 5.2, Render + Cloudflare; 16 dil .po çevirisi dil klasörleriyle

| Kategori | Ağırlık | Skor |
|---|---|---|
| Teknik SEO | %22 | 60 |
| İçerik Kalitesi | %23 | 55 |
| Sayfa İçi SEO | %20 | 50 |
| Şema / Yapısal Veri | %10 | 58 |
| Performans (CWV) | %10 | 55 |
| AI Arama Hazırlığı | %10 | 65 |
| Görseller | %5 | 60 |

**En kritik 5 bulgu:**

1. [High] Başlıklar 106–114 karakter, açıklamalar 187–205; blog yazılarında çift H1, blog ana sayfasında H1 yok
2. [High] Yorum sayısı 352 vs 124, posta kodu 34360 vs 34381, klinik sayfasında saat alanı boş
3. [High] 29 "X açık dişçi" yazısı aynı şablon; /acil-dis-hekimi/ sayfası hekimin kapattığı "acil" niyetini hâlâ hedefliyor
4. [Medium] HSTS yok, csrftoken çerezi Secure değil, blog yazılarında hreflang yok
5. [Medium] /dental-tourism/ sayfası 4 dilde hreflang, x-default Türkçe; diğer 12 dilde sayfa yok mu belirsiz

**Hızlı kazanımlar (saatler içinde):**

- Başlıklar 106–114 karakter, açıklamalar 187–205; blog yazılarında çift H1, blog ana sayfasında H1 yok
- Yorum sayısı 352 vs 124, posta kodu 34360 vs 34381, klinik sayfasında saat alanı boş
- HSTS yok, csrftoken çerezi Secure değil, blog yazılarında hreflang yok
- /dental-tourism/ sayfası 4 dilde hreflang, x-default Türkçe; diğer 12 dilde sayfa yok mu belirsiz
- NAP yazımı üç sitede farklı; yorum sayısı ve "ilk muayene ücretsiz" iddiası doğrulanmalı

## 2. Neler iyi çalışıyor

- HTTPS/TLS 1.3, http→https tek adım 301; robots.txt açık; sitemap geçerli (128 URL, lastmod gerçek tarihlerle)
- Ana sayfada 17 dil + x-default hreflang, dil klasörleri (/en/, /fr/, /de/, /ru/) gerçek çeviri ve doğru <html lang>
- llms.txt var; ChatGPT yönlendirmeleri zaten geliyor (merkezi takip)
- Blog yazılarında Article/BlogPosting + yazar + eğitim bilgisi; 44 yazıdaki 7/24, nöbetçi, gece ifadeleri 22.11'de temizlendi; 13 uzak ilçe/gece yazısı 301
- FAQPage şeması ana sayfada ve klinik sayfasında

## 3. Bulgular (önem sırasıyla)

### [High] Başlıklar 106–114 karakter, açıklamalar 187–205; blog yazılarında çift H1, blog ana sayfasında H1 yok  ·  _Sayfa İçi SEO_

- **Kanıt:** Ana sayfa title 106 / desc 205; /blog/english/dentist-istanbul/ title 114, 2 H1; /blog/en-iyi-disci/sisli-acik-disci/ title 85, 2 H1 (aynı metin iki kez); /blog/ H1 0; /randevu-al/ 14 kelime, desc 198.
- **Neden önemli:** Google başlığı kesip yeniden yazıyor; çift H1 şablon hatası, blog ana sayfası başlıksız. Randevu sayfası neredeyse boş.
- **Öneri:** Şablon: title ≤60 (marka sonda), desc ≤155; blog detay şablonunda başlık bir kez H1 (içerikteki ikinciyi H2 yap veya içerikten çıkar); /blog/ için H1 "Bilgilendirici Yazılar"; randevu sayfasına saat, adres, ne zaman dönüş yapıldığı (hekim metni).
- **Başarı ölçütü:** page_checks: h1_count 1 tüm sayfalarda; title ≤60.
- **Efor:** küçük (saatler)

### [High] Yorum sayısı 352 vs 124, posta kodu 34360 vs 34381, klinik sayfasında saat alanı boş  ·  _Şema / Yapısal Veri_

- **Kanıt:** Blog yazılarında Dentist "Dr. Devrim Biriken Sipahi - Açık Dişçi" aggregateRating 4.9 / reviewCount 352, postalCode 34381; ana sayfa MedicalClinic postalCode 34360; drdevrim 124 yorum; /sisli-dis-klinigi/ OpeningHoursSpecification yalnızca dayOfWeek (opens/closes yok).
- **Neden önemli:** Çelişen sayılar ve adres alanları Google'ın işletme varlığını birleştirmesini zorlaştırır; kendi sayfasında kendi yorum puanı zaten zengin sonuç üretmez, yanlış sayı yalnızca risk.
- **Öneri:** Blog yazılarındaki Dentist bloğunu kaldırıp tek MedicalClinic varlığına (@id) referans verin; aggregateRating'i kaldırın veya GBP'den canlı çekin; posta kodu tek değer (hekim doğrulasın: 34360 mı 34381 mi); klinik sayfasına opens 05:00 / closes 00:00.
- **Başarı ölçütü:** Rich Results Test: tek işletme varlığı, saat alanları tam; üç sitede aynı posta kodu.
- **Efor:** küçük (saatler)

### [High] 29 "X açık dişçi" yazısı aynı şablon; /acil-dis-hekimi/ sayfası hekimin kapattığı "acil" niyetini hâlâ hedefliyor  ·  _İçerik Kalitesi_

- **Kanıt:** /blog/en-iyi-disci/sisli-acik-disci/ 1.297 kelime, komşu ilçe yazıları aynı iskelet (ilçe adı değişiyor); /acil-dis-hekimi/ title "Şişli Acil Diş Hekimi", 274 kelime; drdevrim'de aynı niyet 23.11'de "Diş Ağrısı Tedavisi" yapıldı ve 13 kaldırılan yazıdan biri hâlâ bu sayfaya 301 gidiyor.
- **Neden önemli:** İnce şablon yazılar birbirini kanibalize ediyor; "acil" sayfası hekimin kararına aykırı ve gece sorgularını çekiyor.
- **Öneri:** /acil-dis-hekimi/ → "Diş Ağrısı Tedavisi — Aynı Gün" olarak yeniden adlandır (slug /dis-agrisi-tedavisi/, eski adres 301; acil-disci-istanbul 301'ini de yeni adrese çevir). 29 yazıyı 6–8 bölgesel yazıya birleştirin (Şişli-Osmanbey-Nişantaşı-Mecidiyeköy tek güçlü yazı; Beşiktaş-Etiler-Levent; Kağıthane; Beyoğlu-Taksim-Cihangir; Avrupa yakası merkez), birleşenler 301.
- **Başarı ölçütü:** GSC'de "açık dişçi" sorgularında tek URL; "acil" sorgu gösterimleri 8 haftada düşer.
- **Efor:** orta (1–3 gün)

### [Medium] HSTS yok, csrftoken çerezi Secure değil, blog yazılarında hreflang yok  ·  _Teknik SEO_

- **Kanıt:** Strict-Transport-Security yok; csrftoken Secure bayrağı yok; /blog/... sayfalarında 0 alternate (ana sayfa 18, /dental-tourism/ 5: tr/en/de/nl/x-default); blog TTFB 1,81–1,85 s (ana sayfa 0,38 s).
- **Neden önemli:** HSTS tarayıcı güveni; Secure bayrağı CSRF çerezinin HTTP'de sızmaması için; blog yazıları yalnızca Türkçe olduğu için hreflang eksikliği doğru ama tr + x-default çifti tutarlılık sağlar.
- **Öneri:** SECURE_HSTS_SECONDS=31536000 + includeSubDomains, CSRF_COOKIE_SECURE=True; blog detayına tr + x-default alternate; blog sorgularını (prev/next, kategori) önbelleğe alıp TTFB'yi 0,5 s altına indirin.
- **Başarı ölçütü:** transport_check hsts-missing kapanır; blog TTFB < 0,6 s.
- **Efor:** küçük (saatler)

### [Medium] /dental-tourism/ sayfası 4 dilde hreflang, x-default Türkçe; diğer 12 dilde sayfa yok mu belirsiz  ·  _Hreflang / Programatik_

- **Kanıt:** /dental-tourism/ alternates: tr, en, de, nl + x-default=/dental-tourism/ (Türkçe). Sitede 16 dil var ama bu sayfada 4. Önceki denetimde EN canonical TR adresini gösteriyordu; şimdi canonical kendine dönüyor (düzelmiş).
- **Neden önemli:** Yurt dışı hastaya dönük tek sayfa yarım hreflang kümesiyle İngilizce aramada zayıf kalıyor; dentaltourism.tr ile aynı konuyu iki domainde işlemek "tek konu, tek domain" kuralına aykırı (hekim çapraz link istemiyor; yine de konu çakışması not edilmeli).
- **Öneri:** Ya 16 dilin tamamına hreflang + x-default=en, ya da sayfayı Türkçe'de bırakıp diğer dillerde noindex; dentaltourism.tr ile konu çakışmasını kabul edilen strateji olarak belgeleyin.
- **Başarı ölçütü:** Sayfanın tüm dil sürümlerinde aynı alternate kümesi.
- **Efor:** küçük (saatler)

### [Medium] NAP yazımı üç sitede farklı; yorum sayısı ve "ilk muayene ücretsiz" iddiası doğrulanmalı  ·  _Yerel SEO_

- **Kanıt:** Adres: "Merkez, Abide-i Hürriyet Cd No:148 D:11 kat 4" (dbs) / "Abide-i Hürriyet Caddesi No:148 Kat:4 D:11" (drdevrim) / "… D:11 Kat 4, 34360" (dentaltourism); posta kodu 34360/34381; locality/region alanları ters. /sisli-dis-klinigi/: "ilk muayene ücretsiz, panoramik röntgen" (hekim doğrulamalı).
- **Neden önemli:** GBP–site–rehber tutarlılığı yerel sıralamanın temel sinyali.
- **Öneri:** GBP'deki yazımı birebir alıp üç sitede aynı string'i kullanın; posta kodunu hekim doğrulasın; "ilk muayene ücretsiz" GBP'de de yazıyorsa kalsın, yoksa çıkarın.
- **Başarı ölçütü:** Üç sitenin şema address alanları karakter karakter aynı.
- **Efor:** küçük (saatler)

### [Medium] Laboratuvar verisi yok; ana sayfa 188 KB / 1.247 düğüm, 34 görsel boyutsuz, blog TTFB 1,8 s  ·  _Performans (CWV)_

- **Kanıt:** PSI anahtarı yok (429), Chromium başlamadı. Ölçüm: ana sayfa 188 KB HTML (35 KB gz), 1.247 düğüm, 34 görsel width/height eksik; blog yazısı TTFB 1,81 s (iki ölçümde de).
- **Neden önemli:** Boyutsuz 34 görsel CLS için en somut risk; blog TTFB mobil LCP'yi doğrudan uzatır.
- **Öneri:** Görsellere width/height; blog detay sorgularını önbelleğe alın (prev/next, kategori listesi, SSS); PSI anahtarı ile CrUX takibi.
- **Başarı ölçütü:** CLS < 0,1; blog TTFB < 0,6 s.
- **Efor:** orta (1–3 gün)

### [Medium] "Pazar açık dişçi" niyetine 6 yazı, "Şişli diş kliniği" niyetine klinik sayfası (281 kelime) ve ana sayfa yarışıyor  ·  _Arama Deneyimi (SXO)_

- **Kanıt:** /blog/en-iyi-disci/pazar-acik-disci/, pazar-acik-disci-sisli/, -osmanbey/, -nisantasi/, -kagithane/, cumartesi-acik-disci-pazar-acik-disci/ aynı niyet; /sisli-dis-klinigi/ 281 kelime, ana sayfa 2.418 kelime.
- **Neden önemli:** Google aynı niyet için sitenin hangi sayfasını göstereceğini kararsız bırakır; en çok iniş alan iki sayfadan biri (pazar-acik-disci-sisli) zaten insan trafiği alıyor, dağılmasın.
- **Öneri:** "Pazar açık dişçi Şişli" için tek güçlü sayfa (pazar-acik-disci-sisli) + diğer 5'i ona 301 veya bölge bölümü olarak içine; /sisli-dis-klinigi/ sayfasını klinik turu, ekip, cihazlar, saat, ulaşım ile 800+ kelimeye çıkarın (hekim metni).
- **Başarı ölçütü:** GSC "pazar açık dişçi" tek URL; klinik sayfası "şişli diş kliniği" sorgusunda ilk 10.
- **Efor:** orta (1–3 gün)

### [Low] llms.txt var; agentic P1'de 1 başarısız kontrol; blog yazarı "ekin"  ·  _AI Arama Hazırlığı_

- **Kanıt:** agentic_check summary P1: fail 1, pass 2; BlogPosting author Person name "ekin" (küçük harf, unvan yok).
- **Neden önemli:** E-E-A-T: yazar kimliği zayıf görünüyor; AI motorları yazar varlığını okur.
- **Öneri:** Yazar adını "Dt. Ekin Sipahi" + jobTitle + sameAs (Instagram, dentaltourism hekim sayfası) olarak şemaya ve görünür satıra yazın; P1 başarısız kontrolü agentic.json'dan okuyup kapatın.
- **Başarı ölçütü:** agentic_check P1 fail 0; yazar kutusu her yazıda.
- **Efor:** küçük (saatler)

## 4. Sınırlar

- Performans: PSI anahtarsız istekler 429 döndü, plugin Chromium'u bu makinede başlamadı (exit 127); CWV için yalnızca sunucu süresi, HTML boyutu, DOM ve görsel boyut sinyalleri kullanıldı. Ücretsiz PSI anahtarı eklenince `pagespeed_check.py` ve CrUX alan verisi rapora girer.
- Google Search Console / GA4 API bağlı değil; sıralama ve tıklama yorumları hekimin paylaştığı GSC ekranına dayanır.
- Backlink: Moz/Bing anahtarı yok; profil incelenmedi.
- Tarama örneklemle yapıldı (60 sayfa sınırı); pSEO ailelerinde şablon aynı olduğu için örnek sayfa aileyi temsil eder.
