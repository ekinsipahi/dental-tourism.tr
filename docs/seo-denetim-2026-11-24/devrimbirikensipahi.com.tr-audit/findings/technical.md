# devrimbirikensipahi.com.tr — Teknik SEO

## [Medium] HSTS yok, csrftoken çerezi Secure değil, blog yazılarında hreflang yok

**Kanıt:** Strict-Transport-Security yok; csrftoken Secure bayrağı yok; /blog/... sayfalarında 0 alternate (ana sayfa 18, /dental-tourism/ 5: tr/en/de/nl/x-default); blog TTFB 1,81–1,85 s (ana sayfa 0,38 s).

**Neden önemli:** HSTS tarayıcı güveni; Secure bayrağı CSRF çerezinin HTTP'de sızmaması için; blog yazıları yalnızca Türkçe olduğu için hreflang eksikliği doğru ama tr + x-default çifti tutarlılık sağlar.

**Öneri:** SECURE_HSTS_SECONDS=31536000 + includeSubDomains, CSRF_COOKIE_SECURE=True; blog detayına tr + x-default alternate; blog sorgularını (prev/next, kategori) önbelleğe alıp TTFB'yi 0,5 s altına indirin.

**Başarı ölçütü:** transport_check hsts-missing kapanır; blog TTFB < 0,6 s.  ·  **Efor:** küçük (saatler)
