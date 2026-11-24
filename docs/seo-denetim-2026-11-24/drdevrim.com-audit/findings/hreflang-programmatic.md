# drdevrim.com — Hreflang / Programatik

## [High] Eski 11 ailede hreflang eksik veya 3 dille sınırlı; yeni 11 ailede 18 giriş

**Kanıt:** /disci/sisli/ → 0 hreflang; /en/dentist/sisli/ → 0; /ru/stomatolog/sisli/ → 3 (en, tr, ru); /fr/dentiste/sisli/ → 18 (17 dil + x-default). Aynı konum için 22 sayfa birbirine tutarsız işaret ediyor.

**Neden önemli:** Google hreflang kümelerini karşılıklı doğrular; tek yönlü veya eksik kümeler yok sayılır. Türkçe ana sayfalar (en çok trafik alan aile) hiçbir dil alternatifi bildirmiyor.

**Öneri:** Tüm 22 ailede aynı 17 dil + x-default kümesini üreten tek yardımcı (pseo-i18n.ts) kullanın; TR sayfası x-default olsun. Eski ailelerin şablonlarına eklenmesi tek commit.

**Başarı ölçütü:** Rastgele 10 konum için 22 sayfanın hreflang sayısı 18 ve karşılıklı; GSC "Uluslararası hedefleme" hatası 0.  ·  **Efor:** orta (1–3 gün)
