# drdevrim.com — Teknik SEO

## [Medium] www.drdevrim.com DNS'te yok

**Kanıt:** transport_check: "DNS resolution failed for www.drdevrim.com"; sertifika *.drdevrim.com'u kapsıyor ama kayıt yok.

**Neden önemli:** Elle "www" yazan hasta boş sayfa görür; eski backlinkler www ile verilmişse kaybolur.

**Öneri:** Cloudflare'de www CNAME → apex, Netlify'da www → drdevrim.com 301.

**Başarı ölçütü:** curl -I https://www.drdevrim.com/ → 301 → https://drdevrim.com/  ·  **Efor:** küçük (saatler)
