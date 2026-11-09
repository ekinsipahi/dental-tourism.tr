# dentaltourism.tr

İstanbul'a diş tedavisi için gelen yabancı hastalara yönelik, **16 dilli**, programatik SEO odaklı,
**persona tabanlı kişiselleştirme (ML)** yapan ve **çok klinikli** yapıya hazır Django projesi.

## Kurulum

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# .env dosyasını düzenleyin (ANTHROPIC_API_KEY, e-posta, DB...)
python manage.py migrate
python manage.py seed_data --keywords      # ana klinik, 10 tedavi, İstanbul, yorumlar, 16 dil keyword matrisi
python manage.py apply_ui_translations     # arayüz çevirilerini derler (15 dil hazır)
python manage.py createsuperuser
python manage.py runserver
```

Testler: `python manage.py test tests` (51 test: 16 dil sayfa render, çeviri motoru, slug/301, persona, ML
simülasyonu, arama, yorumlar, schema, favicon, admin içerik blokları)

## Diller

`dental_tourism/languages.py` tek kaynaktır: en (varsayılan, prefix'siz), de, nl, fr, it, es, pl, ru, uk,
ar (RTL), sv, da, no, ro, az, tr. URL segmentleri de çevrilir: `/de/behandlungen/zahnimplantate/`,
`/fr/prix/...`, `/tr/tedaviler/...`.

| Katman | Nerede | Nasıl çevrilir |
|---|---|---|
| Arayüz metinleri (menü, butonlar, başlıklar) | `locale/` | Hazır (15 dil). Yeni metin eklenince: `makemessages -a` → `translate_ui` (AI) veya `locale/_source/<dil>.txt` + `apply_ui_translations` |
| İçerik (blog, tedavi, klinik, hekim, şehir, landing page) | Veritabanı `*Translation` modelleri | Kaydedince/yayınlanınca **otomatik AI çeviri** (Claude) |

## Günlük iş akışı (admin panelinden)

- **Blog:** Admin → Blog → yazıyı istediğiniz dilde yazın (`source_language`), `status = Published` yapın →
  diğer 15 dile arka planda lokalize edilir (dile özel slug, meta title/description, focus keyword).
  Kaynağı düzenlerseniz sadece değişen diller yeniden çevrilir. Bir çeviriyi elle düzeltip
  durumunu **Human reviewed** yaparsanız AI üzerine yazmaz.
- **Görseller:** Klinik → Clinic images → "Toplu görsel yükle". "Slider'da göster" işaretliler ana sayfa
  slider'ına gelir. Logo, favicon, paylaşım görseli: Site settings.
- **Çeviri merkezi:** `/admin/translations/` — model × dil matrisi, tek tıkla eksikleri çevir.
- **Persona paneli:** `/api/dashboard/` — varyant dönüşüm oranları, bandit durumu, ML modeli.
- **Önizleme:** Giriş yapmışken `/?persona=price` (price, fear, shame, urgency, trust, premium, ready,
  skeptic; `?persona=off` kapatır).

## Sayfa metinleri, bölüm sırası ve SEO title'ları (admin)

- **Admin → Site & sayfa metinleri → Content blocks**: Ana sayfadaki tüm başlık/metinler ("Real patients,
  real results" dahil), persona hero metinleri, klinik arama kutusu, SSS (`home-faq` → items) buradan düzenlenir.
  Kaydedince 15 dile otomatik çevrilir; çeviri gelene kadar o dilde hazır (çevrilmiş) varsayılan metin görünür.
- **Bölüm sırası / gizleme**: `home-hero`, `home-treatments`, `home-reviews`, `home-how`, `home-clinic-search`,
  `home-contact`, `home-faq`, `home-cta` bloklarının `order` ve `visible` alanları.
- **SEO title/description**: `seo-home`, `seo-about`, `seo-contact`, `seo-treatments`, `seo-prices`, `seo-clinics`,
  `seo-blog` blokları (title = meta title, subtitle = meta description). Tedavi, blog, klinik, hekim ve landing
  page'lerin meta alanları kendi kayıtlarında.
- Şablona yeni düzenlenebilir metin eklerseniz: `python manage.py sync_content_blocks`.

## Görseller

- Her görsel alanı **dosya yükleme veya link (URL)** kabul eder (klinik kapak/logo, galeri, hekim fotoğrafı,
  önce/sonra, tedavi, blog).
- Toplu: Admin → Clinic images → "Toplu görsel yükle" (çoklu dosya veya her satıra bir link).
- Komut satırından klasör içe aktarma (büyük fotoğraflar 2000px'e küçültülüp optimize edilir):
  `python manage.py import_images /yol/klasor --clinic dr-devrim-sipahi --kind room --alt "..." --hero`
- Favicon: eski sitenin `favicon.ico`'sundan üretildi (`static/favicon.ico`, `static/icons/*`, `/favicon.ico`,
  `/site.webmanifest`). Admin → Site settings → favicon yüklenirse o kullanılır.

## Yorumlar ve klinik profilleri

- **Kendi yorum sistemimiz**: klinik sayfasındaki formdan hasta yorum bırakır → onay kuyruğuna düşer (Admin →
  Reviews → "Onayla ve yayınla"). Ad otomatik "Anna M." formatına kısaltılır, e-posta gösterilmez, IP başına
  günlük limit ve spam tuzağı var; e-posta bir lead ile eşleşirse "Doğrulanmış hasta" rozeti. Klinik yanıt yazabilir.
- **Google / Trustpilot / video yorumları** kaynak linkiyle gösterilir (Admin → Reviews, `source` + `source_url`).
- **SEO**: schema.org `AggregateRating` + `Review` sadece sitemizde toplanan yorumlardan üretilir (Google
  yorumlarını kopyalayıp işaretlemek Google yönergelerine aykırı). Platform birden çok kliniği listelediği için
  bu yorumlar "self-serving" sayılmaz.
- **Profil linkleri**: Klinik formunda Google Business Profile, "Google'da yorum yaz" linki + sınırsız
  "Clinic links" (Instagram, Facebook, YouTube, TikTok, LinkedIn, X, Trustpilot…) → sayfada gösterilir ve
  schema `sameAs` ile Google'a varlık sinyali verir.
- Ana sayfadaki yorumlar tüm yayındaki kliniklerden gelir; `is_featured` olanlar önce.

## Klinik arama

`/clinics/` (ve ana sayfada): isim/hekim/semt araması, şehir, tedavi, konuşulan dil, min. Google puanı,
max. fiyat, sadece doğrulanmış, havalimanı transferi, otel desteği; sıralama (önerilen / puan / fiyat / deneyim).
Filtreli sonuç sayfaları `noindex` (duplicate içerik olmasın), filtresiz liste indexlenir.

## Yeni klinik / hekim eklemek (marketplace)

1. Admin → Users → kullanıcı oluşturun (staff), "clinic owner" izinlerini verin.
2. Admin → Clinics → klinik oluşturun, `owner` = bu kullanıcı, `status = Pending`.
3. Klinik sahibi giriş yaptığında **sadece kendi kliniğini**, hekimlerini, fiyatlarını, yorumlarını ve
   lead'lerini görür. Onaylamak için `status = Approved` (sadece superuser).
4. Tedavi fiyatları klinik sayfasındaki "Clinic treatments" bölümünden; programatik sayfalar
   (`/treatments/<tedavi>/<şehir>/`) klinik listesini otomatik günceller.

## SEO komutları

```bash
python manage.py content generate-treatments        # tedavi sayfası metinleri (AI, kaynak dil)
python manage.py content generate-landing           # tedavi×şehir ve fiyat sayfaları (AI) → noindex kalkar
python manage.py translate_content --missing        # tüm içeriği eksik dillere çevir (senkron)
python manage.py translate_content --status         # dil kapsama tablosu
python manage.py seo keywords-import ahrefs_de.csv --lang de   # Ahrefs/Semrush/Keyword Planner CSV
python manage.py seo keywords-expand --lang de --treatment dental-implants   # AI long-tail önerileri
python manage.py content from-keywords --lang de --limit 5     # sayfası olmayan keyword'lerden blog taslağı
python manage.py seo report --lang de               # keyword kapsama raporu
python manage.py seo audit                          # her dilde on-page SEO denetimi (H1, meta, keyword...)
```

Programatik sayfalar sadece o dilde gerçek içerik olduğunda indexlenir (aksi halde `noindex` + hreflang'de
yer almaz) — ince/duplicate içerik cezası riskine karşı.

## Persona ML (nasıl çalışır)

1. **Inference** (`apps/persona/intent.py`, `engine.py`): reklam kelimesi (`utm_term`), referrer sorgusu
   ve landing URL'si 16 dilli niyet sözlüğüyle puanlanır (ör. "kosten", "цена", "fiyat" → price);
   sayfa içi davranış (fiyat bölümünde kalma süresi, önce/sonra galerisi, video, SSS...) eklenir.
2. **Policy** (`bandit.py`): segment (dil × cihaz × kaynak) bazlı **Thompson Sampling**. Başta tahmin
   edilen persona ağırlıklıdır; veri arttıkça gerçek dönüşüm oranları belirleyici olur. %10 rastgele keşif.
   "unknown" (kişiselleştirilmemiş sayfa) da bir koldur → kişiselleştirmenin işe yarayıp yaramadığı ölçülür.
3. **Supervised model** (`ml.py`): yeterli veri olunca (`.env`: 400 gösterim / 25 dönüşüm) haftalık
   `P(dönüşüm | bağlam, persona)` modeli eğitilir; IPS ile offline değerlendirilir, bandit'ten iyi değilse
   aktif edilmez. Manuel: `python manage.py persona_ml train` / `status`.
4. **Doğrulama simülasyonu** — `python manage.py persona_ml simulate --visitors 3000`: gizli "gerçek persona"lı
   sanal ziyaretçileri gerçek motordan geçirir (veritabanını kirletmez). Son ölçüm: dönüşüm %8.6 (son dönem
   %9.2) — varsayılan sayfa %5, rastgele varyant %3.8; persona tahmini %84 doğru; ML modeli bandit'ten kötüyse
   kendini aktif etmiyor. Aynı kontrol `tests/test_ml_simulation.py` ile her test koşusunda tekrarlanır.
5. Dönüşüm = WhatsApp tıklaması, telefon tıklaması, form gönderimi. Botlar (Googlebot dahil) takip edilmez
   ve her zaman varsayılan içeriği görür (cloaking riski yok; title/meta persona'ya göre değişmez).

## Production

- `.env`: `DEBUG=False`, `DB_ENGINE=postgres`, `CELERY_ENABLED=True`, gerçek `SECRET_KEY`.
- `celery -A dental_tourism worker -l info` ve `celery -A dental_tourism beat -l info`
  (çeviri kuyruğu, haftalık ML eğitimi, günlük ilgili yazılar, saatlik eksik çeviri taraması).
- `python manage.py collectstatic`
- Search Console'a `https://dentaltourism.tr/sitemap.xml` ekleyin.

## Doğrulanması gerekenler

- Eski siteden aktarılan 2 önce/sonra vakası yayında değil: hasta onayı varsa Admin → Before after cases →
  `patient_consent` + `is_published` işaretleyin.
- Fiyatlar (`seed_content.py` → admin'den güncelleyin), İngiltere karşılaştırma fiyatları (`verified=False`).
- Klinik istatistikleri (35+ yıl, 10.000+ hasta, 4.9★) ve gizlilik politikası metni (avukat kontrolü).
- Diğer ülkelerin ortalama fiyatları (Market prices) — eklenmeden fiyat sayfalarında sadece İstanbul görünür.

## Deploy — Render + Supabase (Redis/Celery YOK)

- **Veritabanı:** Supabase PostgreSQL, session pooler (IPv4). Render'da `DATABASE_URL` ortam değişkeni
  (şifredeki özel karakterler percent-encode: `*`→`%2A`, `!`→`%21`). SSL zorunlu (`DB_SSLMODE=require`).
- **Render:** `render.yaml` (Blueprint) + `build.sh` (pip, collectstatic, migrate, createcachetable).
  Gizli değerler (`DATABASE_URL`, `SECRET_KEY`, `ANTHROPIC_API_KEY`) Render panelinden girilir — repoda yok.
- **Lead / webhook koruması** (`apps/tracking/views.py`): `/api/tracking/lead/` yalnızca sitede sayfa açmış
  (oturum çerezli), aynı kökenden (ALLOWED_HOSTS + `TRACKING_ALLOWED_ORIGINS`, ör. `https://drdevrim.com`) gelen,
  bot olmayan isteklere açıktır; oturum başına 3/saat, IP başına 5/saat limit, gizli `website` honeypot alanı,
  16 KB gövde sınırı. `/api/tracking/whatsapp-webhook/` `WHATSAPP_WEBHOOK_SECRET` boşsa kapalıdır (404);
  çağıran `X-Webhook-Secret` (veya `Authorization: Bearer`) başlığı gönderir.
- **Veritabanını Render Postgres'e taşıma** (`scripts/migrate_db_to_render.py`): Render'da aynı bölgede (Frankfurt)
  bir Postgres aç → External Database URL'yi yerel `.env`'e `RENDER_DATABASE_URL=` olarak koy → betik Supabase'den
  yalnızca `public` şemasını `pg_dump` eder, Render'a `pg_restore` eder, tablo satır sayılarını karşılaştırır →
  Render env group'ta `DATABASE_URL` = Internal Database URL, `DB_SSLMODE=prefer` → web yeniden deploy → `--verify`.
  Dump `.migrate_tmp/` altında kalır (gitignore). Dump ile env değişimi arasındaki birkaç dakikanın takip olayları
  Supabase'de kalır; sakin bir saatte yapın.
- **Cache:** veritabanı cache'i (`python manage.py createcachetable`). Arka plan işleri: web sürecinde sınırlı thread havuzu.
- **Zamanlanmış işler:** `python manage.py periodic [--job translations|conversions|related|cleanup|persona]`
  (Render Cron Job veya sistem cron'u).
- **Görseller:** gerçek klinik fotoğrafları `static/img/clinic/` (Render diski geçicidir; `media/` kalıcı değildir).
  Boş veritabanında içerik: `seed_data --keywords`, `import_old_site`, `seed_topics`, `seed_treatment_translations`,
  `seed_profile_translations`, `seed_review_translations`, `seed_media`.

## Ziyaretçi takibi ve kişiselleştirme

- `dt_vid`: kalıcı ziyaretçi kimliği (400 gün çerez + localStorage yedeği). Oturum değişse de aynı kişi tanınır;
  persona geçmişi, niyet skorları ve reklam atfı (gclid/fbclid/utm — ilk ve son dokunuş, localStorage) korunur.
- Tıklamalar (telefon, WhatsApp, CTA, form, video, harita, FAQ, bölüm süreleri) `/api/tracking/event/` ile hem
  dönüşüm takibine hem persona motoruna gider (admin → Tracking / Persona, `/api/dashboard/`).
- Sekme arka plana geçince (`visibilitychange`) sayfa süresi segment olarak gönderilir, geri gelince sayaçlar sıfırdan
  başlar; `time_on_page` sunucuda toplanır (aktif süre). Telefon / WhatsApp / harita tıklamasından sonra siteye dönüş
  `contact_return` olayıdır (`away_seconds`, `likely_contacted` = 8 sn+ uzak kaldı) ve admin → Contact clicks'te
  tıklamanın hemen altında "↩️ Aramadan döndü" olarak görünür.
- `<html data-persona=… data-stage=…>`: persona'ya göre renk/yazı/CTA, huni aşamasına göre
  (awareness → consideration → decision) güven bandı ve mobil iletişim çubuğu.
