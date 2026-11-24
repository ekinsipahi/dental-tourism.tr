# drdevrim.com — Eylem Planı (24.11.2026)

Öncelik: Critical > High > Medium > Low. Her madde: ne, neden, nasıl doğrulanır, efor.

## High

- **Eski 11 ailede hreflang eksik veya 3 dille sınırlı; yeni 11 ailede 18 giriş** — Tüm 22 ailede aynı 17 dil + x-default kümesini üreten tek yardımcı (pseo-i18n.ts) kullanın; TR sayfası x-default olsun. Eski ailelerin şablonlarına eklenmesi tek commit.  
  Doğrulama: Rastgele 10 konum için 22 sayfanın hreflang sayısı 18 ve karşılıklı; GSC "Uluslararası hedefleme" hatası 0.  ·  Efor: orta (1–3 gün)
- **Ölçekli şablon içeriği: 22 aile × 195 konum = 4.290 sayfa, metin %90+ aynı** — Aşama 1: Türkçe 6 aile içinde en zayıf 3'ü (uzman-dis-hekimi, prof-dis-hekimi, estetik-dis-klinigi) noindex veya 410; "disci" + "haftasonu" + "en-iyi-disci" kalsın. Aşama 2: kalan sayfalara konuma özgü gerçek içerik (ulaşım satırı, yakın duraklar, o mahalleden hasta yorumu, hekimin o bölgeye ilişkin notu) ekleyin. Aşama 3: yabancı aileleri 17 ilçe yerine 5–6 merkez ilçeye daraltın.  
  Doğrulama: GSC: indekslenen pSEO sayfa oranı artar (şu an bilinmiyor, GSC "Sayfalar" raporuna bakılmalı); 8 haftada Şişli/Kağıthane/Beşiktaş sayfalarına tıklama artışı.  ·  Efor: büyük (haftalar)
- **Eski ailelerde başlık ve açıklama fazla uzun, abartılı ve bayat sayı içeriyor** — Başlık 55–60, açıklama 140–155 karaktere kısaltın; sayıları kaldırın veya canlı Google puanından besleyin; "Best Dental Clinic Turkey" → "Dentist in Şişli, Istanbul · Family Clinic · 35 Years". Hekim onayı olmayan "10.000+" ifadesini çıkarın.  
  Doğrulama: page_checks: tüm örneklerde title ≤60, desc ≤155; GSC'de Şişli sorgularında CTR 4 haftada artar.  ·  Efor: orta (1–3 gün)

## Medium

- **Aynı sayfada iki Dentist/LocalBusiness varlığı, farklı puan ve bayat yorum sayısı** — Tek Dentist varlığı (@id https://drdevrim.com/#clinic), sayfa şemaları ona referans versin; reviewCount'u GBP'den canlı çekin ya da kaldırın; Person (hekim) worksFor ile bağlansın.  
  Doğrulama: Rich Results Test tek LocalBusiness varlığı gösterir; GSC "Yerel işletme" geliştirme raporunda uyarı 0.  ·  Efor: küçük (saatler)
- **www.drdevrim.com DNS'te yok** — Cloudflare'de www CNAME → apex, Netlify'da www → drdevrim.com 301.  
  Doğrulama: curl -I https://www.drdevrim.com/ → 301 → https://drdevrim.com/  ·  Efor: küçük (saatler)
- **llms.txt yok; AI tarayıcılar için açık politika yok** — llms.txt: klinik, hekimler, saat, adres, hizmetler, en önemli 10 sayfa; robots.txt'ye GPTBot/ClaudeBot/PerplexityBot için açık Allow; Content-Signal başlığı isteğe bağlı.  
  Doğrulama: agentic_check llms_txt pass; 8 haftada AI yönlendirmeli oturum (utm/referrer chatgpt.com, perplexity.ai) merkezi takipte görünür.  ·  Efor: küçük (saatler)
- **Laboratuvar verisi alınamadı; ana sayfa HTML 202 KB / 1.073 DOM düğümü, 5 görsel boyutsuz** — Ücretsiz PageSpeed API anahtarı alıp claude-seo'ya (~/.config/claude-seo/google-api.json) tanımlayın; ana sayfadaki 5 görsele width/height; ana sayfa HTML'ini küçültün (18 dilin satır içi verisi istemciye gidiyor mu kontrol edin).  
  Doğrulama: PSI mobil performans skoru ve CrUX LCP/CLS/INP raporda yer alır; CLS < 0,1.  ·  Efor: orta (1–3 gün)
- **NAP ve saat tutarlı, ancak yorum sayısı ve ortodonti iddiası doğrulanmamış** — GBP'deki gerçek yorum sayısını canlı çekin veya sayıyı kaldırın; ortodonti/Invisalign hizmetini hekim onaylamadıysa menü ve şemadan çıkarın; GBP kategorisi "Diş hekimi" ile şema türü aynı kalsın.  
  Doğrulama: Şema reviewCount = GBP yorum sayısı; GBP hizmet listesi = site hizmet listesi.  ·  Efor: küçük (saatler)
- **"Hafta sonu açık dişçi" niyeti güçlü; "Şişli diş hekimi" için ana sayfa ile /disci/sisli/ birbiriyle yarışıyor** — Şişli için tek hedef sayfa belirleyin (ana sayfa), /disci/sisli/ başlığını "Şişli'de dişçi arayanlar için: mahalleler, ulaşım, randevu" gibi tamamlayıcı açıya çevirin; "pazar açık dişçi" için /haftasonu/sisli/ tek sayfa kalsın.  
  Doğrulama: GSC: "şişli diş hekimi" sorgusunda tek URL görünür, CTR artar.  ·  Efor: orta (1–3 gün)

## Low

- **Sitemap'te 4.343 URL'nin lastmod'u aynı derleme anı** — lastmod'u gerçek değişim tarihinden (şablon/veri commit tarihi) üretin ya da alanı kaldırın; isteğe bağlı: aileler için ayrı sitemap dosyaları + index (GSC'de aile başına indeks takibi).  
  Doğrulama: sitemap_discovery --expand: lastmod_identical_share < 0.5  ·  Efor: küçük (saatler)

## Fazlar

1. **Hafta 1 (Critical/High, küçük efor):** şema birleştirme ve bayat sayılar, başlık/açıklama kısaltma, güvenlik başlıkları, www.
2. **Hafta 2–3:** hreflang tamamlama, kanibalizasyon düzeltmeleri (tek niyet tek sayfa), acil sayfası yeniden adlandırma (dbs), görsel boyutları.
3. **Ay 2 (İçerik & otorite):** şablon sayfa budaması ve konuma özgü içerik; birleştirilen blog yazıları; hekim metinleriyle klinik/randevu sayfaları.
4. **Sürekli:** GSC + pseo_etki haftalık; PSI anahtarıyla CWV; AI referrer takibi.
