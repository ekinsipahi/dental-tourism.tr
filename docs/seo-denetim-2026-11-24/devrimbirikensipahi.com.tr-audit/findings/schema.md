# devrimbirikensipahi.com.tr — Şema / Yapısal Veri

## [High] Yorum sayısı 352 vs 124, posta kodu 34360 vs 34381, klinik sayfasında saat alanı boş

**Kanıt:** Blog yazılarında Dentist "Dr. Devrim Biriken Sipahi - Açık Dişçi" aggregateRating 4.9 / reviewCount 352, postalCode 34381; ana sayfa MedicalClinic postalCode 34360; drdevrim 124 yorum; /sisli-dis-klinigi/ OpeningHoursSpecification yalnızca dayOfWeek (opens/closes yok).

**Neden önemli:** Çelişen sayılar ve adres alanları Google'ın işletme varlığını birleştirmesini zorlaştırır; kendi sayfasında kendi yorum puanı zaten zengin sonuç üretmez, yanlış sayı yalnızca risk.

**Öneri:** Blog yazılarındaki Dentist bloğunu kaldırıp tek MedicalClinic varlığına (@id) referans verin; aggregateRating'i kaldırın veya GBP'den canlı çekin; posta kodu tek değer (hekim doğrulasın: 34360 mı 34381 mi); klinik sayfasına opens 05:00 / closes 00:00.

**Başarı ölçütü:** Rich Results Test: tek işletme varlığı, saat alanları tam; üç sitede aynı posta kodu.  ·  **Efor:** küçük (saatler)
