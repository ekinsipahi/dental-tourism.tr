# drdevrim.com — Performans (CWV)

## [Medium] Laboratuvar verisi alınamadı; ana sayfa HTML 202 KB / 1.073 DOM düğümü, 5 görsel boyutsuz

**Kanıt:** PageSpeed API anahtarı yok (anahtarsız istek 429), Chromium başlatılamadı (headless shell exit 127). Ölçülen: TTFB 0,40–0,66 s; ana sayfa HTML 202 KB (35 KB gz), 1.073 düğüm; pSEO sayfası 77 KB / 368 düğüm; ana sayfada 5 görsel width/height eksik (CLS riski).

**Neden önemli:** CWV alan verisi olmadan öncelik sırası tahmindir; CLS için boyutsuz görseller somut risk.

**Öneri:** Ücretsiz PageSpeed API anahtarı alıp claude-seo'ya (~/.config/claude-seo/google-api.json) tanımlayın; ana sayfadaki 5 görsele width/height; ana sayfa HTML'ini küçültün (18 dilin satır içi verisi istemciye gidiyor mu kontrol edin).

**Başarı ölçütü:** PSI mobil performans skoru ve CrUX LCP/CLS/INP raporda yer alır; CLS < 0,1.  ·  **Efor:** orta (1–3 gün)
