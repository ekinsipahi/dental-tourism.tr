# dentaltourism.tr — Performans (CWV)

## [Medium] Laboratuvar verisi yok; soğuk istekte TTFB 2,6 s görüldü

**Kanıt:** PageSpeed API anahtarı yok (429), Chromium başlatılamadı. Ölçüm: /treatments/dental-implants/ ilk istek TTFB 2,60 s, ikinci 0,28 s; ana sayfa 0,25–0,29 s. Ana sayfa 1.123 DOM düğümü, 19 görsel boyutsuz.

**Neden önemli:** Render free/soğuk başlatma veya önbellek dolmadan gelen ilk ziyaretçi 2–3 s bekler; LCP alan verisini bu istekler bozar.

**Öneri:** Önbellek ısıtma (uptime ping 5 dk) veya Render planı; 19 görsele width/height; PSI anahtarıyla CrUX alan verisini rapora alın.

**Başarı ölçütü:** TTFB p75 < 0,8 s; CrUX LCP "iyi".  ·  **Efor:** orta (1–3 gün)
