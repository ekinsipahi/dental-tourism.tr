# Üç site SEO denetimi — özet (24.11.2026)

| Site | Skor | İş tipi | En kritik 3 |
|---|---|---|---|
| drdevrim.com | **64** | Yerel hizmet (aile diş kliniği, Şişli) + programatik konum sayfaları; Nuxt 4 SSR, Netlify + Cloudflare | [High] Eski 11 ailede hreflang eksik veya 3 dille sınırlı; yeni 11 ailede 18 giriş · [High] Ölçekli şablon içeriği: 22 aile × 195 konum = 4.290 sayfa, metin %90+ aynı · [High] Eski ailelerde başlık ve açıklama fazla uzun, abartılı ve bayat sayı içeriyor |
| dentaltourism.tr | **74** | Sağlık turizmi (yurt dışı hasta), 17 dil; Django 5.1, Render + Cloudflare | [High] Semt ve ülke sayfaları 17 dilde şablon: 13 semt × 17 dil + ülke sayfaları, yüksek benzerlik · [Medium] Her sayfada 216–250 link ve 117 görsel: 17 dilli gezinme ve bayrak görselleri sayfayı şişiriyor · [Medium] HSTS zayıf (30 gün, includeSubDomains yok), CSP ve Permissions-Policy yok, www DNS'te yok |
| devrimbirikensipahi.com.tr | **57** | Kurumsal klinik sitesi + blog (yerel, marka); Django 5.2, Render + Cloudflare; 16 dil .po çevirisi dil klasörleriyle | [High] Başlıklar 106–114 karakter, açıklamalar 187–205; blog yazılarında çift H1, blog ana sayfasında H1 yok · [High] Yorum sayısı 352 vs 124, posta kodu 34360 vs 34381, klinik sayfasında saat alanı boş · [High] 29 "X açık dişçi" yazısı aynı şablon; /acil-dis-hekimi/ sayfası hekimin kapattığı "acil" niyetini hâlâ hedefliyor |

Üç sitede ortak: (1) aynı kliniğin NAP/saat/yorum sayısı üç sitede farklı yazılıyor → tek doğru yazım (GBP) her yere; (2) laboratuvar CWV verisi için ücretsiz PageSpeed API anahtarı gerekiyor; (3) www alt alanları hiçbirinde çözümlenmiyor; (4) şablon konum/dil sayfaları (drdevrim 4.290, dentaltourism ~400, dbs 29 yazı) en büyük içerik riski.

Ayrıntı: `<site>-audit/FULL-AUDIT-REPORT.md`, `ACTION-PLAN.md`, `findings/*.md`, `audit-data.json`, ham veri `data/`.
