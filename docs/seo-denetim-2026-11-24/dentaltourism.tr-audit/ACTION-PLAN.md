# dentaltourism.tr — Eylem Planı (24.11.2026)

Öncelik: Critical > High > Medium > Low. Her madde: ne, neden, nasıl doğrulanır, efor.

## High

- **Semt ve ülke sayfaları 17 dilde şablon: 13 semt × 17 dil + ülke sayfaları, yüksek benzerlik** — Semt sayfalarını 5 dile (en, de, ru, ar, fr) indirin; kalan dillerde noindex veya ülke sayfasına birleştirin. Ülke sayfalarına ülkeye özgü somut bölüm (uçuş süresi, belge, sigorta/ödeme notları hekimden) ekleyin.  
  Doğrulama: GSC "Sayfalar" raporunda "Taranmış, dizine eklenmemiş" oranı düşer; semt sayfalarına organik iniş artar.  ·  Efor: büyük (haftalar)

## Medium

- **Her sayfada 216–250 link ve 117 görsel: 17 dilli gezinme ve bayrak görselleri sayfayı şişiriyor** — Dil seçiciyi tek <select> veya JS ile açılan menüye alın (hreflang link etiketleri zaten var); bayrakları CSS sprite veya tek SVG yapın; footer'daki tam dil listesi yalnızca ana sayfada kalsın.  
  Doğrulama: page_checks: sayfa başına link < 120, görsel < 40.  ·  Efor: orta (1–3 gün)
- **HSTS zayıf (30 gün, includeSubDomains yok), CSP ve Permissions-Policy yok, www DNS'te yok** — HSTS max-age=31536000; includeSubDomains; Permissions-Policy ekle; www için DNS + 301 ve sertifikaya www ekle (Render otomatik verir).  
  Doğrulama: transport_check: hsts-weak ve www-sibling-unreachable bulguları kapanır.  ·  Efor: küçük (saatler)
- **Laboratuvar verisi yok; soğuk istekte TTFB 2,6 s görüldü** — Önbellek ısıtma (uptime ping 5 dk) veya Render planı; 19 görsele width/height; PSI anahtarıyla CrUX alan verisini rapora alın.  
  Doğrulama: TTFB p75 < 0,8 s; CrUX LCP "iyi".  ·  Efor: orta (1–3 gün)
- **Dönüşüm yolu WhatsApp ağırlıklı; "fiyat" niyetli sorgularda fiyatsız politika beklentiyi karşılamıyor** — Fiyat sorgularını hedefleyen sayfalarda başlığa "fiyatı neyin belirlediği" açısı, sayfada "neden sabit fiyat listesi yok, 24 saatte yazılı teklif" bloğu (hekim cümleleriyle); WhatsApp yanında e-posta formu ve geri arama saati seçimi.  
  Doğrulama: GSC fiyat sorgularında CTR ve sayfada kalma süresi artar; WhatsApp tıklama/oturum oranı merkezi takipte yükselir.  ·  Efor: orta (1–3 gün)

## Low

- **MedicalClinic openingHours "Mo-Su 05:00-23:59", kardeş sitelerde 05:00-00:00; Organization adı alan adı** — Saat 05:00-00:00; addressLocality "Şişli", addressRegion "İstanbul" olarak üç sitede aynı; Organization adı "Dr. Dt. Devrim Biriken Sipahi Dental Clinic" + alternateName "dentaltourism.tr".  
  Doğrulama: Üç sitenin şemaları yan yana aynı NAP ve saat.  ·  Efor: küçük (saatler)
- **llms.txt var; AI botlar için robots politikası ve içerik sinyali belirtilmemiş** — robots.txt'ye GPTBot, ClaudeBot, PerplexityBot, Google-Extended için açık Allow; her blog yazısında 40–60 kelimelik "kısa cevap" paragrafı; llms.txt'yi 5 blog yazısıyla güncel tutun.  
  Doğrulama: Merkezi takipte AI referrer oturumları (chatgpt.com, perplexity.ai) 8 haftada görünür.  ·  Efor: küçük (saatler)
- **Ülke sayfalarında hreflang yalnızca kendi dili; x-default yok** — Ülke sayfalarına x-default (kendisi) ekleyin; İngilizce karşılığı olan ülkelerde en ↔ yerel dil çiftini bağlayın.  
  Doğrulama: Her ülke sayfasında ≥2 alternate (self + x-default).  ·  Efor: küçük (saatler)

## Fazlar

1. **Hafta 1 (Critical/High, küçük efor):** şema birleştirme ve bayat sayılar, başlık/açıklama kısaltma, güvenlik başlıkları, www.
2. **Hafta 2–3:** hreflang tamamlama, kanibalizasyon düzeltmeleri (tek niyet tek sayfa), acil sayfası yeniden adlandırma (dbs), görsel boyutları.
3. **Ay 2 (İçerik & otorite):** şablon sayfa budaması ve konuma özgü içerik; birleştirilen blog yazıları; hekim metinleriyle klinik/randevu sayfaları.
4. **Sürekli:** GSC + pseo_etki haftalık; PSI anahtarıyla CWV; AI referrer takibi.
