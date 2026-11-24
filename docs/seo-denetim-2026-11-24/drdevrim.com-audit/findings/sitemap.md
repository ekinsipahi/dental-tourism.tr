# drdevrim.com — Site Haritası

## [Low] Sitemap'te 4.343 URL'nin lastmod'u aynı derleme anı

**Kanıt:** lastmod_identical_share 1.0 (2026-11-23T19:01:24Z). Google değişmemiş sayfalara "değişti" sinyali almayı güvenilmez sayar ve lastmod'u yok sayar.

**Neden önemli:** Yeni dil sayfaları ve değişen şablonlar için öncelikli tarama şansı kaybolur.

**Öneri:** lastmod'u gerçek değişim tarihinden (şablon/veri commit tarihi) üretin ya da alanı kaldırın; isteğe bağlı: aileler için ayrı sitemap dosyaları + index (GSC'de aile başına indeks takibi).

**Başarı ölçütü:** sitemap_discovery --expand: lastmod_identical_share < 0.5  ·  **Efor:** küçük (saatler)
