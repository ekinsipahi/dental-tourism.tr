# dentaltourism.tr — SEO Denetim Raporu (24.11.2026)

Araç: claude-seo v2.6.2 (yalnızca ücretsiz araçlar; PageSpeed API anahtarı ve Chromium olmadan laboratuvar CWV verisi alınamadı). Tarama: sitemap, robots, 10–13 canlı sayfa, JSON-LD, hreflang, güvenlik başlıkları, sunucu süresi. Rapor hekim için Türkçe. Ham veri: data/.

## 1. Yönetici özeti

**SEO Sağlık Skoru: 74/100**  ·  İş tipi: Sağlık turizmi (yurt dışı hasta), 17 dil; Django 5.1, Render + Cloudflare

| Kategori | Ağırlık | Skor |
|---|---|---|
| Teknik SEO | %22 | 78 |
| İçerik Kalitesi | %23 | 74 |
| Sayfa İçi SEO | %20 | 72 |
| Şema / Yapısal Veri | %10 | 80 |
| Performans (CWV) | %10 | 65 |
| AI Arama Hazırlığı | %10 | 72 |
| Görseller | %5 | 70 |

**En kritik 5 bulgu:**

1. [High] Semt ve ülke sayfaları 17 dilde şablon: 13 semt × 17 dil + ülke sayfaları, yüksek benzerlik
2. [Medium] Her sayfada 216–250 link ve 117 görsel: 17 dilli gezinme ve bayrak görselleri sayfayı şişiriyor
3. [Medium] HSTS zayıf (30 gün, includeSubDomains yok), CSP ve Permissions-Policy yok, www DNS'te yok
4. [Medium] Laboratuvar verisi yok; soğuk istekte TTFB 2,6 s görüldü
5. [Medium] Dönüşüm yolu WhatsApp ağırlıklı; "fiyat" niyetli sorgularda fiyatsız politika beklentiyi karşılamıyor

**Hızlı kazanımlar (saatler içinde):**

- HSTS zayıf (30 gün, includeSubDomains yok), CSP ve Permissions-Policy yok, www DNS'te yok
- MedicalClinic openingHours "Mo-Su 05:00-23:59", kardeş sitelerde 05:00-00:00; Organization adı alan adı
- llms.txt var; AI botlar için robots politikası ve içerik sinyali belirtilmemiş
- Ülke sayfalarında hreflang yalnızca kendi dili; x-default yok

## 2. Neler iyi çalışıyor

- Hreflang eksiksiz: 17 dil + x-default, her sayfada 18 <link rel=alternate>, href'ler dil klasörleriyle tutarlı; blog yazılarında yalnızca en + x-default (doğru, çevirisi yok)
- Başlık/açıklama uzunlukları iyi (51–60 / 139–157); her sayfada tek H1; canonical kendine dönüyor
- Gerçek uzman içerik: blog yazısı 3.464 kelime, hekim yazar + MedicalWebPage/lastReviewed şeması, SSS şeması, breadcrumb; rehber 1.857 kelime; hakkımızda 1.643 kelime
- llms.txt var, robots.txt temiz, sitemap geçerli (1.284 URL), HTTPS/TLS 1.3, X-Frame-Options DENY
- Sunucu yanıtı ısınmış durumda 0,25–0,29 s, HTML 20 KB gz

## 3. Bulgular (önem sırasıyla)

### [High] Semt ve ülke sayfaları 17 dilde şablon: 13 semt × 17 dil + ülke sayfaları, yüksek benzerlik  ·  _İçerik Kalitesi_

- **Kanıt:** /dental-clinic/taksim/ 1.587 kelime, 250 link; aynı şablon 13 semt × 17 dil = 221 sayfa; ülke sayfaları (/bg/dentalen-turizam-ot/bulgaria/ 1.453 kelime) ülke adı dışında birbirine çok yakın. Sitemap'in yaklaşık yarısı bu şablonlardan.
- **Neden önemli:** Google "ölçekli içerik" politikası dil × konum çarpımlarını hedefler; semt sayfaları yurt dışı hastanın gerçek sorusunu (Taksim'e yakınlık) karşılıyor ama 17 dilde aynı metin olması indekslenmeyi düşürür.
- **Öneri:** Semt sayfalarını 5 dile (en, de, ru, ar, fr) indirin; kalan dillerde noindex veya ülke sayfasına birleştirin. Ülke sayfalarına ülkeye özgü somut bölüm (uçuş süresi, belge, sigorta/ödeme notları hekimden) ekleyin.
- **Başarı ölçütü:** GSC "Sayfalar" raporunda "Taranmış, dizine eklenmemiş" oranı düşer; semt sayfalarına organik iniş artar.
- **Efor:** büyük (haftalar)

### [Medium] Her sayfada 216–250 link ve 117 görsel: 17 dilli gezinme ve bayrak görselleri sayfayı şişiriyor  ·  _Sayfa İçi SEO_

- **Kanıt:** Ana sayfa 229 link / 117 görsel (52'si boş alt'lı bayrak PNG, her bayrak 2 kez); /treatments/dental-implants/ 216 link / 91 görsel; dil seçici tüm sayfalarda açık 17 bağlantı.
- **Neden önemli:** Link başına aktarılan değer düşer, ana içerik oranı azalır; tarayıcı 100 küsur gezinme linkini her sayfada yeniden işler.
- **Öneri:** Dil seçiciyi tek <select> veya JS ile açılan menüye alın (hreflang link etiketleri zaten var); bayrakları CSS sprite veya tek SVG yapın; footer'daki tam dil listesi yalnızca ana sayfada kalsın.
- **Başarı ölçütü:** page_checks: sayfa başına link < 120, görsel < 40.
- **Efor:** orta (1–3 gün)

### [Medium] HSTS zayıf (30 gün, includeSubDomains yok), CSP ve Permissions-Policy yok, www DNS'te yok  ·  _Teknik SEO_

- **Kanıt:** Strict-Transport-Security: max-age=2592000; CSP yok; Permissions-Policy yok; www.dentaltourism.tr çözümlenmiyor; sertifika yalnızca apex (SAN 1).
- **Neden önemli:** Güvenlik başlıkları doğrudan sıralama etkeni değil ama tarayıcı güven göstergeleri ve Lighthouse "best practices" puanını etkiler; www kaybı kullanıcı kaybıdır.
- **Öneri:** HSTS max-age=31536000; includeSubDomains; Permissions-Policy ekle; www için DNS + 301 ve sertifikaya www ekle (Render otomatik verir).
- **Başarı ölçütü:** transport_check: hsts-weak ve www-sibling-unreachable bulguları kapanır.
- **Efor:** küçük (saatler)

### [Medium] Laboratuvar verisi yok; soğuk istekte TTFB 2,6 s görüldü  ·  _Performans (CWV)_

- **Kanıt:** PageSpeed API anahtarı yok (429), Chromium başlatılamadı. Ölçüm: /treatments/dental-implants/ ilk istek TTFB 2,60 s, ikinci 0,28 s; ana sayfa 0,25–0,29 s. Ana sayfa 1.123 DOM düğümü, 19 görsel boyutsuz.
- **Neden önemli:** Render free/soğuk başlatma veya önbellek dolmadan gelen ilk ziyaretçi 2–3 s bekler; LCP alan verisini bu istekler bozar.
- **Öneri:** Önbellek ısıtma (uptime ping 5 dk) veya Render planı; 19 görsele width/height; PSI anahtarıyla CrUX alan verisini rapora alın.
- **Başarı ölçütü:** TTFB p75 < 0,8 s; CrUX LCP "iyi".
- **Efor:** orta (1–3 gün)

### [Medium] Dönüşüm yolu WhatsApp ağırlıklı; "fiyat" niyetli sorgularda fiyatsız politika beklentiyi karşılamıyor  ·  _Arama Deneyimi (SXO)_

- **Kanıt:** Guest-post ve GSC verisi: "all on 4 istanbul", "dental implants turkey price" tipi sorgular; sayfalar fiyat vermiyor (politika). /treatments/dental-implants/ "fixed written quote" vaadiyle WhatsApp'a yönlendiriyor; form var, telefon yok.
- **Neden önemli:** Fiyat arayan kullanıcı fiyat görmeyince hemen çıkar; politika korunacaksa beklentiyi başlıkta yönetmek gerekir.
- **Öneri:** Fiyat sorgularını hedefleyen sayfalarda başlığa "fiyatı neyin belirlediği" açısı, sayfada "neden sabit fiyat listesi yok, 24 saatte yazılı teklif" bloğu (hekim cümleleriyle); WhatsApp yanında e-posta formu ve geri arama saati seçimi.
- **Başarı ölçütü:** GSC fiyat sorgularında CTR ve sayfada kalma süresi artar; WhatsApp tıklama/oturum oranı merkezi takipte yükselir.
- **Efor:** orta (1–3 gün)

### [Low] MedicalClinic openingHours "Mo-Su 05:00-23:59", kardeş sitelerde 05:00-00:00; Organization adı alan adı  ·  _Şema / Yapısal Veri_

- **Kanıt:** Ana sayfa Dentist/MedicalClinic openingHours ["Mo-Su 05:00-23:59"]; drdevrim ve devrimbirikensipahi 05:00–00:00. Organization name "dentaltourism.tr", logo var; address locality "Istanbul", region "Şişli" (kardeş sitede tersi).
- **Neden önemli:** Üç sitede aynı kliniğin saat ve adres alanları farklı yazılıyor; varlık birleştirmesi (knowledge graph) zorlaşır.
- **Öneri:** Saat 05:00-00:00; addressLocality "Şişli", addressRegion "İstanbul" olarak üç sitede aynı; Organization adı "Dr. Dt. Devrim Biriken Sipahi Dental Clinic" + alternateName "dentaltourism.tr".
- **Başarı ölçütü:** Üç sitenin şemaları yan yana aynı NAP ve saat.
- **Efor:** küçük (saatler)

### [Low] llms.txt var; AI botlar için robots politikası ve içerik sinyali belirtilmemiş  ·  _AI Arama Hazırlığı_

- **Kanıt:** robots.txt: User-agent: * (AI botlara özel satır yok); agentic_check P1 3 bilgi 3 geçti. E1 ve E2 yazıları alıntılanabilir yapıda (soru başlıkları, kısa cevaplar, SSS şeması).
- **Neden önemli:** Yurt dışı hasta araştırmasının önemli kısmı ChatGPT/Perplexity'de geçiyor; açık izin ve speakable alanları alıntı şansını artırır.
- **Öneri:** robots.txt'ye GPTBot, ClaudeBot, PerplexityBot, Google-Extended için açık Allow; her blog yazısında 40–60 kelimelik "kısa cevap" paragrafı; llms.txt'yi 5 blog yazısıyla güncel tutun.
- **Başarı ölçütü:** Merkezi takipte AI referrer oturumları (chatgpt.com, perplexity.ai) 8 haftada görünür.
- **Efor:** küçük (saatler)

### [Low] Ülke sayfalarında hreflang yalnızca kendi dili; x-default yok  ·  _Hreflang / Programatik_

- **Kanıt:** /bg/dentalen-turizam-ot/bulgaria/ → 1 hreflang (bg). Ülke sayfasının başka dili olmaması doğru; ama x-default eksik ve İngilizce "from Bulgaria" karşılığı yoksa İngilizce arayan Bulgar kullanıcı eşleşmiyor.
- **Neden önemli:** Küçük etki; tutarlılık için.
- **Öneri:** Ülke sayfalarına x-default (kendisi) ekleyin; İngilizce karşılığı olan ülkelerde en ↔ yerel dil çiftini bağlayın.
- **Başarı ölçütü:** Her ülke sayfasında ≥2 alternate (self + x-default).
- **Efor:** küçük (saatler)

## 4. Sınırlar

- Performans: PSI anahtarsız istekler 429 döndü, plugin Chromium'u bu makinede başlamadı (exit 127); CWV için yalnızca sunucu süresi, HTML boyutu, DOM ve görsel boyut sinyalleri kullanıldı. Ücretsiz PSI anahtarı eklenince `pagespeed_check.py` ve CrUX alan verisi rapora girer.
- Google Search Console / GA4 API bağlı değil; sıralama ve tıklama yorumları hekimin paylaştığı GSC ekranına dayanır.
- Backlink: Moz/Bing anahtarı yok; profil incelenmedi.
- Tarama örneklemle yapıldı (60 sayfa sınırı); pSEO ailelerinde şablon aynı olduğu için örnek sayfa aileyi temsil eder.
