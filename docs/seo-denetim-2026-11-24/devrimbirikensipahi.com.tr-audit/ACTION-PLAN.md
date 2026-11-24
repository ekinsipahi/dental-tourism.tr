# devrimbirikensipahi.com.tr — Eylem Planı (24.11.2026)

Öncelik: Critical > High > Medium > Low. Her madde: ne, neden, nasıl doğrulanır, efor.

## High

- **Başlıklar 106–114 karakter, açıklamalar 187–205; blog yazılarında çift H1, blog ana sayfasında H1 yok** — Şablon: title ≤60 (marka sonda), desc ≤155; blog detay şablonunda başlık bir kez H1 (içerikteki ikinciyi H2 yap veya içerikten çıkar); /blog/ için H1 "Bilgilendirici Yazılar"; randevu sayfasına saat, adres, ne zaman dönüş yapıldığı (hekim metni).  
  Doğrulama: page_checks: h1_count 1 tüm sayfalarda; title ≤60.  ·  Efor: küçük (saatler)
- **Yorum sayısı 352 vs 124, posta kodu 34360 vs 34381, klinik sayfasında saat alanı boş** — Blog yazılarındaki Dentist bloğunu kaldırıp tek MedicalClinic varlığına (@id) referans verin; aggregateRating'i kaldırın veya GBP'den canlı çekin; posta kodu tek değer (hekim doğrulasın: 34360 mı 34381 mi); klinik sayfasına opens 05:00 / closes 00:00.  
  Doğrulama: Rich Results Test: tek işletme varlığı, saat alanları tam; üç sitede aynı posta kodu.  ·  Efor: küçük (saatler)
- **29 "X açık dişçi" yazısı aynı şablon; /acil-dis-hekimi/ sayfası hekimin kapattığı "acil" niyetini hâlâ hedefliyor** — /acil-dis-hekimi/ → "Diş Ağrısı Tedavisi — Aynı Gün" olarak yeniden adlandır (slug /dis-agrisi-tedavisi/, eski adres 301; acil-disci-istanbul 301'ini de yeni adrese çevir). 29 yazıyı 6–8 bölgesel yazıya birleştirin (Şişli-Osmanbey-Nişantaşı-Mecidiyeköy tek güçlü yazı; Beşiktaş-Etiler-Levent; Kağıthane; Beyoğlu-Taksim-Cihangir; Avrupa yakası merkez), birleşenler 301.  
  Doğrulama: GSC'de "açık dişçi" sorgularında tek URL; "acil" sorgu gösterimleri 8 haftada düşer.  ·  Efor: orta (1–3 gün)

## Medium

- **HSTS yok, csrftoken çerezi Secure değil, blog yazılarında hreflang yok** — SECURE_HSTS_SECONDS=31536000 + includeSubDomains, CSRF_COOKIE_SECURE=True; blog detayına tr + x-default alternate; blog sorgularını (prev/next, kategori) önbelleğe alıp TTFB'yi 0,5 s altına indirin.  
  Doğrulama: transport_check hsts-missing kapanır; blog TTFB < 0,6 s.  ·  Efor: küçük (saatler)
- **/dental-tourism/ sayfası 4 dilde hreflang, x-default Türkçe; diğer 12 dilde sayfa yok mu belirsiz** — Ya 16 dilin tamamına hreflang + x-default=en, ya da sayfayı Türkçe'de bırakıp diğer dillerde noindex; dentaltourism.tr ile konu çakışmasını kabul edilen strateji olarak belgeleyin.  
  Doğrulama: Sayfanın tüm dil sürümlerinde aynı alternate kümesi.  ·  Efor: küçük (saatler)
- **NAP yazımı üç sitede farklı; yorum sayısı ve "ilk muayene ücretsiz" iddiası doğrulanmalı** — GBP'deki yazımı birebir alıp üç sitede aynı string'i kullanın; posta kodunu hekim doğrulasın; "ilk muayene ücretsiz" GBP'de de yazıyorsa kalsın, yoksa çıkarın.  
  Doğrulama: Üç sitenin şema address alanları karakter karakter aynı.  ·  Efor: küçük (saatler)
- **Laboratuvar verisi yok; ana sayfa 188 KB / 1.247 düğüm, 34 görsel boyutsuz, blog TTFB 1,8 s** — Görsellere width/height; blog detay sorgularını önbelleğe alın (prev/next, kategori listesi, SSS); PSI anahtarı ile CrUX takibi.  
  Doğrulama: CLS < 0,1; blog TTFB < 0,6 s.  ·  Efor: orta (1–3 gün)
- **"Pazar açık dişçi" niyetine 6 yazı, "Şişli diş kliniği" niyetine klinik sayfası (281 kelime) ve ana sayfa yarışıyor** — "Pazar açık dişçi Şişli" için tek güçlü sayfa (pazar-acik-disci-sisli) + diğer 5'i ona 301 veya bölge bölümü olarak içine; /sisli-dis-klinigi/ sayfasını klinik turu, ekip, cihazlar, saat, ulaşım ile 800+ kelimeye çıkarın (hekim metni).  
  Doğrulama: GSC "pazar açık dişçi" tek URL; klinik sayfası "şişli diş kliniği" sorgusunda ilk 10.  ·  Efor: orta (1–3 gün)

## Low

- **llms.txt var; agentic P1'de 1 başarısız kontrol; blog yazarı "ekin"** — Yazar adını "Dt. Ekin Sipahi" + jobTitle + sameAs (Instagram, dentaltourism hekim sayfası) olarak şemaya ve görünür satıra yazın; P1 başarısız kontrolü agentic.json'dan okuyup kapatın.  
  Doğrulama: agentic_check P1 fail 0; yazar kutusu her yazıda.  ·  Efor: küçük (saatler)

## Fazlar

1. **Hafta 1 (Critical/High, küçük efor):** şema birleştirme ve bayat sayılar, başlık/açıklama kısaltma, güvenlik başlıkları, www.
2. **Hafta 2–3:** hreflang tamamlama, kanibalizasyon düzeltmeleri (tek niyet tek sayfa), acil sayfası yeniden adlandırma (dbs), görsel boyutları.
3. **Ay 2 (İçerik & otorite):** şablon sayfa budaması ve konuma özgü içerik; birleştirilen blog yazıları; hekim metinleriyle klinik/randevu sayfaları.
4. **Sürekli:** GSC + pseo_etki haftalık; PSI anahtarıyla CWV; AI referrer takibi.
