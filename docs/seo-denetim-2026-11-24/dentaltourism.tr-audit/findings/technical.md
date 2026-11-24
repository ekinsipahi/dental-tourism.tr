# dentaltourism.tr — Teknik SEO

## [Medium] HSTS zayıf (30 gün, includeSubDomains yok), CSP ve Permissions-Policy yok, www DNS'te yok

**Kanıt:** Strict-Transport-Security: max-age=2592000; CSP yok; Permissions-Policy yok; www.dentaltourism.tr çözümlenmiyor; sertifika yalnızca apex (SAN 1).

**Neden önemli:** Güvenlik başlıkları doğrudan sıralama etkeni değil ama tarayıcı güven göstergeleri ve Lighthouse "best practices" puanını etkiler; www kaybı kullanıcı kaybıdır.

**Öneri:** HSTS max-age=31536000; includeSubDomains; Permissions-Policy ekle; www için DNS + 301 ve sertifikaya www ekle (Render otomatik verir).

**Başarı ölçütü:** transport_check: hsts-weak ve www-sibling-unreachable bulguları kapanır.  ·  **Efor:** küçük (saatler)
