# drdevrim.com — SEO Denetim Raporu (24.11.2026)

Araç: claude-seo v2.6.2 (yalnızca ücretsiz araçlar; PageSpeed API anahtarı ve Chromium olmadan laboratuvar CWV verisi alınamadı). Tarama: sitemap, robots, 10–13 canlı sayfa, JSON-LD, hreflang, güvenlik başlıkları, sunucu süresi. Rapor hekim için Türkçe. Ham veri: data/.

## 1. Yönetici özeti

**SEO Sağlık Skoru: 64/100**  ·  İş tipi: Yerel hizmet (aile diş kliniği, Şişli) + programatik konum sayfaları; Nuxt 4 SSR, Netlify + Cloudflare

| Kategori | Ağırlık | Skor |
|---|---|---|
| Teknik SEO | %22 | 72 |
| İçerik Kalitesi | %23 | 58 |
| Sayfa İçi SEO | %20 | 62 |
| Şema / Yapısal Veri | %10 | 70 |
| Performans (CWV) | %10 | 60 |
| AI Arama Hazırlığı | %10 | 55 |
| Görseller | %5 | 80 |

**En kritik 5 bulgu:**

1. [High] Eski 11 ailede hreflang eksik veya 3 dille sınırlı; yeni 11 ailede 18 giriş
2. [High] Ölçekli şablon içeriği: 22 aile × 195 konum = 4.290 sayfa, metin %90+ aynı
3. [High] Eski ailelerde başlık ve açıklama fazla uzun, abartılı ve bayat sayı içeriyor
4. [Medium] Aynı sayfada iki Dentist/LocalBusiness varlığı, farklı puan ve bayat yorum sayısı
5. [Medium] www.drdevrim.com DNS'te yok

**Hızlı kazanımlar (saatler içinde):**

- Aynı sayfada iki Dentist/LocalBusiness varlığı, farklı puan ve bayat yorum sayısı
- www.drdevrim.com DNS'te yok
- llms.txt yok; AI tarayıcılar için açık politika yok
- NAP ve saat tutarlı, ancak yorum sayısı ve ortodonti iddiası doğrulanmamış
- Sitemap'te 4.343 URL'nin lastmod'u aynı derleme anı

## 2. Neler iyi çalışıyor

- HTTPS, HSTS (1 yıl, includeSubDomains), TLS 1.3, tek adımlı http→https 301
- robots.txt temiz, tek sitemap (4.343 URL, geçerli, kopya yok); silinen 2.233 sayfa doğru biçimde 410 + noindex
- Her sayfada tek H1, kendine dönen canonical, index/follow; JSON-LD geçerli (4 blok, 0 hata)
- Yeni 11 dil ailesinde tam hreflang kümesi (17 dil + x-default), Dentist + FAQPage + BreadcrumbList şeması, 05:00–00:00 saatleri tutarlı
- Görsellerde alt eksik yok (yalnızca favicon boş alt), pSEO sayfalarında width/height tam, ilk görsel lazy
- Sunucu yanıtı 0,40–0,66 s, HTML sıkıştırılmış (ana sayfa 35 KB gz)

## 3. Bulgular (önem sırasıyla)

### [High] Eski 11 ailede hreflang eksik veya 3 dille sınırlı; yeni 11 ailede 18 giriş  ·  _Hreflang / Programatik_

- **Kanıt:** /disci/sisli/ → 0 hreflang; /en/dentist/sisli/ → 0; /ru/stomatolog/sisli/ → 3 (en, tr, ru); /fr/dentiste/sisli/ → 18 (17 dil + x-default). Aynı konum için 22 sayfa birbirine tutarsız işaret ediyor.
- **Neden önemli:** Google hreflang kümelerini karşılıklı doğrular; tek yönlü veya eksik kümeler yok sayılır. Türkçe ana sayfalar (en çok trafik alan aile) hiçbir dil alternatifi bildirmiyor.
- **Öneri:** Tüm 22 ailede aynı 17 dil + x-default kümesini üreten tek yardımcı (pseo-i18n.ts) kullanın; TR sayfası x-default olsun. Eski ailelerin şablonlarına eklenmesi tek commit.
- **Başarı ölçütü:** Rastgele 10 konum için 22 sayfanın hreflang sayısı 18 ve karşılıklı; GSC "Uluslararası hedefleme" hatası 0.
- **Efor:** orta (1–3 gün)

### [High] Ölçekli şablon içeriği: 22 aile × 195 konum = 4.290 sayfa, metin %90+ aynı  ·  _İçerik Kalitesi_

- **Kanıt:** /disci/sisli/ 788 kelime, /disci/sisli/nisantasi/ aynı şablon; /fr/dentiste/sisli/ 633 kelime; konum adı ve kuş uçuşu mesafe dışında sayfalar birbirinin kopyası. Google spam politikası "doorway" tanımı birebir bu yapı; 22.11 budaması riski 38→17 ilçeye indirdi ama yapı aynı.
- **Neden önemli:** Core update dönemlerinde bu tür bölümler topluca değer kaybeder; indekslenmeyen binlerce sayfa tarama bütçesini yer. Dünkü GSC verisi: 4.290 sayfanın yalnızca bir avucu tıklama alıyor (Kadıköy mahalleleri, Şişli).
- **Öneri:** Aşama 1: Türkçe 6 aile içinde en zayıf 3'ü (uzman-dis-hekimi, prof-dis-hekimi, estetik-dis-klinigi) noindex veya 410; "disci" + "haftasonu" + "en-iyi-disci" kalsın. Aşama 2: kalan sayfalara konuma özgü gerçek içerik (ulaşım satırı, yakın duraklar, o mahalleden hasta yorumu, hekimin o bölgeye ilişkin notu) ekleyin. Aşama 3: yabancı aileleri 17 ilçe yerine 5–6 merkez ilçeye daraltın.
- **Başarı ölçütü:** GSC: indekslenen pSEO sayfa oranı artar (şu an bilinmiyor, GSC "Sayfalar" raporuna bakılmalı); 8 haftada Şişli/Kağıthane/Beşiktaş sayfalarına tıklama artışı.
- **Efor:** büyük (haftalar)

### [High] Eski ailelerde başlık ve açıklama fazla uzun, abartılı ve bayat sayı içeriyor  ·  _Sayfa İçi SEO_

- **Kanıt:** /en/dentist/sisli/ title 90 karakter ("Best Dental Clinic Turkey"), description 235; /ru/stomatolog/sisli/nisantasi/ title 77 / desc 231; /haftasonu/sisli/ title 78 / desc 183; ana sayfa title 72 / desc 186; her yerde "124 yorum", "10.000+ vaka/hasta".
- **Neden önemli:** Google 60 karakteri aşan başlığı kısaltır veya yeniden yazar; "Best … Turkey" gibi üstünlük iddiaları tıklama getirmiyor ve sağlık alanında güven düşürüyor. "124 yorum" sayısı bayat (hekim doğruladı), "10.000+ vaka" doğrulanmamış iddia.
- **Öneri:** Başlık 55–60, açıklama 140–155 karaktere kısaltın; sayıları kaldırın veya canlı Google puanından besleyin; "Best Dental Clinic Turkey" → "Dentist in Şişli, Istanbul · Family Clinic · 35 Years". Hekim onayı olmayan "10.000+" ifadesini çıkarın.
- **Başarı ölçütü:** page_checks: tüm örneklerde title ≤60, desc ≤155; GSC'de Şişli sorgularında CTR 4 haftada artar.
- **Efor:** orta (1–3 gün)

### [Medium] Aynı sayfada iki Dentist/LocalBusiness varlığı, farklı puan ve bayat yorum sayısı  ·  _Şema / Yapısal Veri_

- **Kanıt:** Ana sayfa: "Dr. Dt. Devrim Biriken Sipahi Diş Kliniği" (ratingValue 5.0, reviewCount 124) + "Dr. Dt. Devrim Biriken Sipahi" (ratingValue 5, 124); /disci/sisli/ ve /iletisim/ sayfalarında da iki blok. @id yok, varlıklar birleşmiyor.
- **Neden önemli:** Google aynı işletmeyi iki kez görür; AggregateRating için "kendi sayfanda kendi işletmen" durumunda zengin sonuç zaten gösterilmez, bayat sayı güven kaybı. Yerel paket sinyali bulanıklaşır.
- **Öneri:** Tek Dentist varlığı (@id https://drdevrim.com/#clinic), sayfa şemaları ona referans versin; reviewCount'u GBP'den canlı çekin ya da kaldırın; Person (hekim) worksFor ile bağlansın.
- **Başarı ölçütü:** Rich Results Test tek LocalBusiness varlığı gösterir; GSC "Yerel işletme" geliştirme raporunda uyarı 0.
- **Efor:** küçük (saatler)

### [Medium] www.drdevrim.com DNS'te yok  ·  _Teknik SEO_

- **Kanıt:** transport_check: "DNS resolution failed for www.drdevrim.com"; sertifika *.drdevrim.com'u kapsıyor ama kayıt yok.
- **Neden önemli:** Elle "www" yazan hasta boş sayfa görür; eski backlinkler www ile verilmişse kaybolur.
- **Öneri:** Cloudflare'de www CNAME → apex, Netlify'da www → drdevrim.com 301.
- **Başarı ölçütü:** curl -I https://www.drdevrim.com/ → 301 → https://drdevrim.com/
- **Efor:** küçük (saatler)

### [Medium] llms.txt yok; AI tarayıcılar için açık politika yok  ·  _AI Arama Hazırlığı_

- **Kanıt:** https://drdevrim.com/llms.txt → 404; robots.txt yalnızca User-agent: * (AI botlara özel satır yok). agentic_check P1 bulguları "info" düzeyinde.
- **Neden önemli:** ChatGPT/Perplexity alıntıları kardeş sitede (devrimbirikensipahi) zaten geliyor; drdevrim'de klinik özetini makine okunur vermek alıntı şansını artırır. Google için llms.txt etkisizdir, diğer motorlar için ucuz sinyal.
- **Öneri:** llms.txt: klinik, hekimler, saat, adres, hizmetler, en önemli 10 sayfa; robots.txt'ye GPTBot/ClaudeBot/PerplexityBot için açık Allow; Content-Signal başlığı isteğe bağlı.
- **Başarı ölçütü:** agentic_check llms_txt pass; 8 haftada AI yönlendirmeli oturum (utm/referrer chatgpt.com, perplexity.ai) merkezi takipte görünür.
- **Efor:** küçük (saatler)

### [Medium] Laboratuvar verisi alınamadı; ana sayfa HTML 202 KB / 1.073 DOM düğümü, 5 görsel boyutsuz  ·  _Performans (CWV)_

- **Kanıt:** PageSpeed API anahtarı yok (anahtarsız istek 429), Chromium başlatılamadı (headless shell exit 127). Ölçülen: TTFB 0,40–0,66 s; ana sayfa HTML 202 KB (35 KB gz), 1.073 düğüm; pSEO sayfası 77 KB / 368 düğüm; ana sayfada 5 görsel width/height eksik (CLS riski).
- **Neden önemli:** CWV alan verisi olmadan öncelik sırası tahmindir; CLS için boyutsuz görseller somut risk.
- **Öneri:** Ücretsiz PageSpeed API anahtarı alıp claude-seo'ya (~/.config/claude-seo/google-api.json) tanımlayın; ana sayfadaki 5 görsele width/height; ana sayfa HTML'ini küçültün (18 dilin satır içi verisi istemciye gidiyor mu kontrol edin).
- **Başarı ölçütü:** PSI mobil performans skoru ve CrUX LCP/CLS/INP raporda yer alır; CLS < 0,1.
- **Efor:** orta (1–3 gün)

### [Medium] NAP ve saat tutarlı, ancak yorum sayısı ve ortodonti iddiası doğrulanmamış  ·  _Yerel SEO_

- **Kanıt:** Adres "Abide-i Hürriyet Caddesi No:148 Kat:4 D:11", telefon +905055771883, 05:00–00:00 × 7 gün her yerde aynı (iyi). Ana sayfa meta: "ortodonti" (hekim sorusu 25 açık); "124 yorum" bayat; hasMap ve sameAs var.
- **Neden önemli:** GBP ile site arasında yorum sayısı ve hizmet listesi uyuşmazsa yerel paket güveni düşer.
- **Öneri:** GBP'deki gerçek yorum sayısını canlı çekin veya sayıyı kaldırın; ortodonti/Invisalign hizmetini hekim onaylamadıysa menü ve şemadan çıkarın; GBP kategorisi "Diş hekimi" ile şema türü aynı kalsın.
- **Başarı ölçütü:** Şema reviewCount = GBP yorum sayısı; GBP hizmet listesi = site hizmet listesi.
- **Efor:** küçük (saatler)

### [Medium] "Hafta sonu açık dişçi" niyeti güçlü; "Şişli diş hekimi" için ana sayfa ile /disci/sisli/ birbiriyle yarışıyor  ·  _Arama Deneyimi (SXO)_

- **Kanıt:** Ana sayfa title "Şişli Diş Hekimi", /disci/sisli/ title "Şişli Dişçi … Diş Hekimi", /en-iyi-disci/sisli/, /uzman-dis-hekimi/sisli/ aynı niyete 4 sayfa. GSC (22–23.11): "şişli diş hekimi" 11 gösterim 0 tıklama, "nişantaşı diş hekimi" 11/0.
- **Neden önemli:** Aynı niyete birden çok sayfa, Google'ın hangisini göstereceğini sürekli değiştirmesine (kanibalizasyon) ve düşük CTR'ye yol açar.
- **Öneri:** Şişli için tek hedef sayfa belirleyin (ana sayfa), /disci/sisli/ başlığını "Şişli'de dişçi arayanlar için: mahalleler, ulaşım, randevu" gibi tamamlayıcı açıya çevirin; "pazar açık dişçi" için /haftasonu/sisli/ tek sayfa kalsın.
- **Başarı ölçütü:** GSC: "şişli diş hekimi" sorgusunda tek URL görünür, CTR artar.
- **Efor:** orta (1–3 gün)

### [Low] Sitemap'te 4.343 URL'nin lastmod'u aynı derleme anı  ·  _Site Haritası_

- **Kanıt:** lastmod_identical_share 1.0 (2026-11-23T19:01:24Z). Google değişmemiş sayfalara "değişti" sinyali almayı güvenilmez sayar ve lastmod'u yok sayar.
- **Neden önemli:** Yeni dil sayfaları ve değişen şablonlar için öncelikli tarama şansı kaybolur.
- **Öneri:** lastmod'u gerçek değişim tarihinden (şablon/veri commit tarihi) üretin ya da alanı kaldırın; isteğe bağlı: aileler için ayrı sitemap dosyaları + index (GSC'de aile başına indeks takibi).
- **Başarı ölçütü:** sitemap_discovery --expand: lastmod_identical_share < 0.5
- **Efor:** küçük (saatler)

## 4. Sınırlar

- Performans: PSI anahtarsız istekler 429 döndü, plugin Chromium'u bu makinede başlamadı (exit 127); CWV için yalnızca sunucu süresi, HTML boyutu, DOM ve görsel boyut sinyalleri kullanıldı. Ücretsiz PSI anahtarı eklenince `pagespeed_check.py` ve CrUX alan verisi rapora girer.
- Google Search Console / GA4 API bağlı değil; sıralama ve tıklama yorumları hekimin paylaştığı GSC ekranına dayanır.
- Backlink: Moz/Bing anahtarı yok; profil incelenmedi.
- Tarama örneklemle yapıldı (60 sayfa sınırı); pSEO ailelerinde şablon aynı olduğu için örnek sayfa aileyi temsil eder.
