# devrimbirikensipahi.com.tr — Performans (CWV)

## [Medium] Laboratuvar verisi yok; ana sayfa 188 KB / 1.247 düğüm, 34 görsel boyutsuz, blog TTFB 1,8 s

**Kanıt:** PSI anahtarı yok (429), Chromium başlamadı. Ölçüm: ana sayfa 188 KB HTML (35 KB gz), 1.247 düğüm, 34 görsel width/height eksik; blog yazısı TTFB 1,81 s (iki ölçümde de).

**Neden önemli:** Boyutsuz 34 görsel CLS için en somut risk; blog TTFB mobil LCP'yi doğrudan uzatır.

**Öneri:** Görsellere width/height; blog detay sorgularını önbelleğe alın (prev/next, kategori listesi, SSS); PSI anahtarı ile CrUX takibi.

**Başarı ölçütü:** CLS < 0,1; blog TTFB < 0,6 s.  ·  **Efor:** orta (1–3 gün)
