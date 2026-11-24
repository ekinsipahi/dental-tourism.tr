# dentaltourism.tr — Şema / Yapısal Veri

## [Low] MedicalClinic openingHours "Mo-Su 05:00-23:59", kardeş sitelerde 05:00-00:00; Organization adı alan adı

**Kanıt:** Ana sayfa Dentist/MedicalClinic openingHours ["Mo-Su 05:00-23:59"]; drdevrim ve devrimbirikensipahi 05:00–00:00. Organization name "dentaltourism.tr", logo var; address locality "Istanbul", region "Şişli" (kardeş sitede tersi).

**Neden önemli:** Üç sitede aynı kliniğin saat ve adres alanları farklı yazılıyor; varlık birleştirmesi (knowledge graph) zorlaşır.

**Öneri:** Saat 05:00-00:00; addressLocality "Şişli", addressRegion "İstanbul" olarak üç sitede aynı; Organization adı "Dr. Dt. Devrim Biriken Sipahi Dental Clinic" + alternateName "dentaltourism.tr".

**Başarı ölçütü:** Üç sitenin şemaları yan yana aynı NAP ve saat.  ·  **Efor:** küçük (saatler)
