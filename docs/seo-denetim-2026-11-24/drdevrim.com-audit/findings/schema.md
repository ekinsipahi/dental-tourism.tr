# drdevrim.com — Şema / Yapısal Veri

## [Medium] Aynı sayfada iki Dentist/LocalBusiness varlığı, farklı puan ve bayat yorum sayısı

**Kanıt:** Ana sayfa: "Dr. Dt. Devrim Biriken Sipahi Diş Kliniği" (ratingValue 5.0, reviewCount 124) + "Dr. Dt. Devrim Biriken Sipahi" (ratingValue 5, 124); /disci/sisli/ ve /iletisim/ sayfalarında da iki blok. @id yok, varlıklar birleşmiyor.

**Neden önemli:** Google aynı işletmeyi iki kez görür; AggregateRating için "kendi sayfanda kendi işletmen" durumunda zengin sonuç zaten gösterilmez, bayat sayı güven kaybı. Yerel paket sinyali bulanıklaşır.

**Öneri:** Tek Dentist varlığı (@id https://drdevrim.com/#clinic), sayfa şemaları ona referans versin; reviewCount'u GBP'den canlı çekin ya da kaldırın; Person (hekim) worksFor ile bağlansın.

**Başarı ölçütü:** Rich Results Test tek LocalBusiness varlığı gösterir; GSC "Yerel işletme" geliştirme raporunda uyarı 0.  ·  **Efor:** küçük (saatler)
