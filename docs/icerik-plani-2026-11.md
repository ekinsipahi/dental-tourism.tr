# İçerik planı — 20 uzman yazı + 9 klinik sayfası (Kasım–Aralık 2026)

Kaynak: danışman listesindeki 54 soru (10 Türkçe hasta sorusu, 17 klinik uzman sorusu, 12 İngilizce turist sorusu,
10 klinik işleyiş sorusu, 5 ilk makale). Her soru tek bir parçaya bağlandı; hiçbir soru açıkta kalmadı (bkz. §4).

## Kurallar

- **Site rolleri:** Türkçe klinik karar yazıları → **drdevrim.com/blog/**. İngilizce turist yazıları → **dentaltourism.tr/blog/** (kaynak dil EN; hekim kararı 19.11: şimdilik yalnızca İngilizce, çeviri yok). Klinik işleyiş sayfaları (saatler, acil, ilk muayene, sterilizasyon, tedavi listesi) → **devrimbirikensipahi.com.tr**.
- **Bir konu, bir dilde, tek alan adında.** Aynı konunun Türkçesi drdevrim'de, İngilizcesi dentaltourism'de olabilir; aynı dilde iki kopya olmaz. Çakışan eski sayfalar 301 ile yeni parçaya gider (§5).
- **Rehber varsa yazı açılmaz:** soru mevcut bir `/guide/` konusunu karşılıyorsa hekim cevabı rehber gövdesine girer; blog yalnızca soru biçimli, tarihli, imzalı yazılar için.
- **Klinik iddia yalnızca hekimden.** Her parçanın "Hekimden" listesi cevaplanmadan yazı yazılmaz. Rakam (yıl, vaka sayısı, süre) yalnızca hekimin verdiği rakamdır. Fiyat, yüzde tasarruf, otel/uçuş/transfer vaadi yok. "En iyi", "garantili", "ağrısız" gibi üstünlük ve kesinlik ifadeleri yok (sağlık tanıtım mevzuatı).
- **Her yazıda:** ilk paragrafta doğrudan cevap; "hangi durumda yapılmaz / önerilmez" bölümü; hekimin kendi karar kriteri; gerçek, kimliksiz bir gözlem; yazar kutusu (Dr. Dt. Devrim Biriken Sipahi / Dt. Ekin Sipahi, tek Person kimliği); yayın ve güncelleme tarihi; 2–4 iç link; sonda nazik tek CTA.
- **Fotoğraf:** stok görsel yok. Her parçada klinikten gerçek fotoğraf (cihaz, ortam, ekip, belge). Hasta görüntüsü ve radyografi yalnızca yazılı onamla ve kimliksiz; önce/sonra görselleri bilgilendirme amaçlı ve abartısız kullanılır.
- Her cevap sesli mesaj olabilir (5–10 dk / parça). Cevabın başına kimin konuştuğu: **[Devrim]** ya da **[Ekin]**.

## 0. Gün 0 — altyapı (19–20 Kasım, Claude; hekim girdisi gerekmez)

1. **drdevrim.com blog:** Nuxt Content v3 (bağımlılık kurulu, modül kapalı) → `content/blog/*.md`, `pages/blog/[slug].vue`, Article + Person şeması, yazar kutusu, dateModified, ilgili pSEO ailesine ve hizmet sayfasına link bloğu, sitemap'e ekleme. "Çok Yakında" sayfası gerçek listeye döner.
2. **dentaltourism.tr blog:** kategoriler (`planning-your-trip`, `safety-and-quality`, `treatment-decisions`) 17 dilde; yazar = `reviewed_by` Doctor; FAQPage şeması yazı başına tekil (tedavi/paket/fiyat üçlüsündeki tekrar kaldırılır).
3. **devrimbirikensipahi.com.tr:** dört işleyiş sayfası için şablon ve URL'ler (§2 B1–B4), başlık ve marka güncellemesi, yönlendirme sayfalarındaki `canonical=drdevrim.com` kalıntıları kaldırılır, `/dental-tourism/` sayfası dentaltourism.tr'ye link verir.
4. **Varlık tutarlılığı (3 site):** tek resmi ad (`Dr. Dt. Devrim Biriken Sipahi`), `alternateName: Dr. Devrim`; tek Person `@id` (drdevrim.com/doktorlar/#devrim ve #ekin) her yazıda author/reviewedBy; sameAs = GBP/Maps (tek link), Instagram, YouTube, diğer iki site; aynı adres, koordinat, telefon, yorum sayısı; `knowsAbout` listesi B4'teki tedavi listesiyle aynı; `openingHoursSpecification` B1'deki gerçek saatlerle aynı.
5. **Link akışını tersine çevirme:** drdevrim'in yabancı dilli pSEO sayfaları (en/de/ru/uk/bg) ve hizmet sayfaları → aynı dildeki dentaltourism tedavi/rehber/yazı sayfasına bağlamsal blok. Her yeni dentaltourism yazısı yayınlanınca ilgili drdevrim sayfalarına link eklenir.
6. **Ölçüm:** Bing Webmaster Tools + IndexNow (dentaltourism, drdevrim); GSC servis hesabı gelince `Keyword.clicks_28d / impressions_28d` içe aktarımı.

## 1. Takvim (Pazar yok; tarihler öneri, kaydırılabilir)

| Gün | Tarih | Parça | Site | URL |
|---|---|---|---|---|
| 1 | Cmt 21.11 | B1 Çalışma saatleri, hafta sonu ve acil | devrimbirikensipahi | /calisma-saatleri-ve-acil/ |
| 2 | Pzt 23.11 | D11 + E11 Hekim sayfaları (biyografi, eğitim, yaklaşım) | drdevrim + dentaltourism | /doktorlar/ · /clinics/dr-devrim-sipahi/ · /dentists/… |
| 3 | Sal 24.11 | B2 İlk muayene nasıl geçer | devrimbirikensipahi | /ilk-muayene/ |
| 4 | Çar 25.11 | B3 Sterilizasyon, kayıt ve takip | devrimbirikensipahi | /sterilizasyon-ve-hasta-guvenligi/ |
| 5 | Per 26.11 | B4 + B5 Uyguladığımız / uygulamadığımız tedaviler; implant sistemleri | devrimbirikensipahi (+ dentaltourism tedavi sayfası) | /tedaviler/ · /implant · /treatments/dental-implants/ |
| 6 | Cum 27.11 | D1 Dişi çekmek mi, kurtarmak mı? | drdevrim | /blog/dis-cekimi-mi-kanal-tedavisi-mi/ |
| 7 | Cmt 28.11 | D4 Diş ağrısında ne zaman acil? | drdevrim | /blog/dis-agrisi-ne-zaman-acil/ |
| 8 | Pzt 30.11 | D2 Çürük var, ağrı yok: dolgu mu kanal mı? | drdevrim | /blog/curuk-var-agri-yok-dolgu-mu-kanal-mi/ |
| 9 | Sal 1.12 | D8 Dişleri kestirmeden estetik: bonding, lamina, zirkonyum | drdevrim | /blog/disleri-kestirmeden-estetik/ |
| 10 | Çar 2.12 | D5 İmplant mı, köprü mü? | drdevrim | /blog/implant-mi-kopru-mu/ |
| 11 | ~~Per 3.12~~ **20.11 yayında** | ~~E7 Röntgeninizle seyahatten önce plan~~ ✅ | dentaltourism | /blog/planning-your-trip/send-your-dental-x-ray-for-a-preliminary-assessment/ |
| 12 | Cum 4.12 | E4 Dental implants in Turkey: how many visits? | dentaltourism | /blog/planning-your-trip/dental-implants-in-turkey-how-many-visits/ |
| 13 | ~~Cmt 5.12~~ **19.11 yayında** | ~~E1 Is it safe to get dental implants in Turkey?~~ ✅ | dentaltourism | /blog/safety-and-quality/is-it-safe-to-get-dental-implants-in-turkey/ |
| 14 | Pzt 7.12 | E8 Why do some dentists refuse crowns on healthy teeth? | dentaltourism | /blog/treatment-decisions/why-dentists-refuse-crowns-on-healthy-teeth/ |
| 15 | Sal 8.12 | E6 If my implant fails after I return home | dentaltourism (+ rehber gövdesi) | /blog/safety-and-quality/dental-implant-failed-after-returning-home/ · /guide/dental-guarantee-aftercare/ |
| 16 | Çar 9.12 | D6 Tek diş eksikliğinde implant süreci | drdevrim | /blog/tek-dis-implant-sureci/ |
| 17 | Per 10.12 | D9 Sağlam dişe kaplama yapılır mı? Hollywood smile | drdevrim | /blog/saglam-dise-kaplama-yapilir-mi/ |
| 18 | Cum 11.12 | E9 Risks of 20 zirconia crowns | dentaltourism | /blog/treatment-decisions/risks-of-20-zirconia-crowns-in-turkey/ |
| 19 | Cmt 12.12 | E2 How to find a trustworthy dentist in Istanbul | dentaltourism | /blog/safety-and-quality/how-to-find-a-trustworthy-dentist-in-istanbul/ |
| 20 | Pzt 14.12 | D3 Kanal tedavili diş tekrar ağrıyorsa | drdevrim | /blog/kanal-tedavili-dis-tekrar-agriyor/ |
| 21 | Sal 15.12 | E3 What is included in a dental quote in Turkey | dentaltourism (+ /prices/ özeti) | /blog/planning-your-trip/what-is-included-in-a-dental-quote-in-turkey/ |
| 22 | Çar 16.12 | D7 Diş eti sağlığı ve implant | drdevrim | /blog/dis-eti-sagligi-ve-implant/ |
| 23 | Per 17.12 | E5 How many days in Istanbul for crowns and veneers | dentaltourism | /blog/planning-your-trip/how-many-days-in-istanbul-for-dental-crowns/ |
| 24 | Cum 18.12 | E10 Emergency dental care while visiting Istanbul | dentaltourism | /blog/planning-your-trip/emergency-dentist-while-visiting-istanbul/ |
| 25 | Cmt 19.12 | D10 İstanbul'da diş hekimi seçerken | drdevrim | /blog/istanbulda-dis-hekimi-secerken/ |

Çeviriler (RU/DE/BG/FR) her E-parçası yayınlandıktan sonra otomatik üretilir, yayından önce göz atılır. Sonraki 16 yazı ölçüm sonucuna göre seçilir (danışmanın "20 yazı, sonra ölç" ilkesi).

## 2. Parçalar

### B1 — Çalışma saatleri, hafta sonu ve acil hasta kabulü (devrimbirikensipahi, TR; EN/DE/NL özeti why-us sayfalarında)
Soruları: TR3 (Şişli'de pazar açık diş hekimi var mı), K2 (günler, saatler, pazar ve acil süreç).
Hekimden: gerçek çalışma günleri ve saatleri; pazar ve resmî tatil politikası; acil hastanın gece/hafta sonu ne yapacağı (kim açar, hangi numara, ne kadar sürede dönüş); acilde ilk seansta ne yapılır, ne yapılmaz; randevusuz gelen hastaya yaklaşım.
Fotoğraf: dış cephe ve tabela (GBP için de), bina girişi, resepsiyon, bekleme alanı.
Bağlantılar: drdevrim `haftasonu/*` ve `acil` sayfaları buraya link verir; GBP saatleri ve 3 sitedeki `openingHoursSpecification` bu sayfayla aynı olur (şu an drdevrim 07:00–23:00 × 7 gün yazıyor — doğrulanacak).
Temizlik: devrimbirikensipahi `/blog/en-iyi-disci/pazar-acik-disci-*` yazıları (yaklaşık 55 ince sayfa) → karar: 301 bu sayfaya ya da noindex (§5).

### D11 + E11 — Hekim sayfaları (drdevrim /doktorlar/ ana kaynak; dentaltourism /clinics/dr-devrim-sipahi/ ve /dentists/* aynı metnin EN'i; devrimbirikensipahi /neden-biz/ kısa özet)
Soruları: K9 (eğitim, deneyim, klinik yaklaşım).
Hekimden [Devrim]: mezuniyet yılı ve okul (Ankara Üniv.), Marmara'daki ağız-diş-çene radyolojisi eğitiminin yılı ve niteliği (doktora mı, uzmanlık mı — unvan buna göre yazılır), 35+ yılın kaba kırılımı (nerede, ne kadar), ağırlıklı yaptığı tedaviler, yapmadığı tedaviler, bir hastaya tedavi önermeyi reddettiği gerçek bir örnek. [Ekin]: mezuniyet (2025, İstanbul Kent Üniv.), ilgi alanları, dijital araçlar (tarayıcı, tasarım yazılımı), annesiyle ortak planlamanın hastaya ne kattığı. Konuşulan diller.
Fotoğraf: iki hekimin portreleri (aynı ışık, aynı fon), birlikte çalışırken bir kare, diplomalar/sertifikalar (okunur, kimlik numarası kapatılmış), ekip fotoğrafı.
Not: bu sayfa tüm yazıların yazar kutusunun kaynağıdır; şemadaki `alumniOf`, `hasCredential`, `knowsAbout` buradan doldurulur.

### B2 — İlk muayene nasıl geçer (devrimbirikensipahi, TR)
Soruları: K3 (ilk muayene, radyografi, tedavi planlaması).
Hekimden: ilk randevu kaç dakika; hangi görüntüleme ne zaman (panoramik, periapikal, 3D tomografi — cihaz adı); radyoloji eğitiminin teşhiste somut katkısına bir örnek; plan nasıl anlatılır (yazılı mı, seçenekli mi); ilk seansta tedaviye başlanır mı; ikinci görüş isteyen hastaya yaklaşım.
Fotoğraf: görüntüleme cihazı, muayene odası, ekranda (kimliksiz) bir radyografi, plan anlatılırken masa/tablet.

### B3 — Sterilizasyon, kayıt ve takip (devrimbirikensipahi, TR; EN özeti dentaltourism /about/)
Soruları: K10 (sterilizasyon, kayıt, takip süreçleri).
Hekimden: otoklav sınıfı ve kontrol yöntemi (indikatör, periyodik test), tek kullanımlık malzeme politikası, aletlerin poşetleme/izlenebilirlik düzeni, hasta kaydı ve görüntülerin saklanması, kontrol randevusu düzeni, uzaktaki hasta için takip yöntemi.
Fotoğraf: otoklav, poşetlenmiş alet seti, indikatör şeridi, sterilizasyon alanı, kayıt yazılımı ekranı (kimliksiz).

### B4 + B5 — Uyguladığımız ve uygulamadığımız tedaviler; implant sistemleri (devrimbirikensipahi /tedaviler/ ve /implant; aynı gerçekler dentaltourism /treatments/dental-implants/ gövdesine)
Soruları: K1 (hangi tedaviler yapılıyor, hangileri yapılmıyor), K6 (implant marka/sistem, greft ne zaman).
Hekimden: tam tedavi listesi; yapılmayan tedaviler (ortodonti? çocuk? genel anestezi?) — bu cevap 3 sitedeki `knowsAbout` çelişkisini kapatır (drdevrim "Ortodonti" yazıyor, dentaltourism "yapılmıyor" varsayıyor); kullanılan implant markaları ve neden; yaklaşık kaç yıldır / kaç implant (yuvarlak, gerçek); cerrahi rehber ve tomografi kullanımı; kemik grefti/sinüs lift hangi durumlarda; hastaya verilen implant belgesi.
Fotoğraf: implant kutuları ve hasta belgesi örneği, cerrahi rehber, tomografi ekranı, implant seti.

### D1 — Dişi çekmek mi, kurtarmak mı? Hangi durumlarda kanal tedavisi yeterlidir? (drdevrim, TR — ilk makale 1)
Soruları: TR2 (çektirmeden kurtarmak mümkün mü), TR5 (kanal mı çekim mi), E1 (kök ucunda iltihap görülen her dişe kanal yapılır mı), E3 (yarısı kırılan diş kurtarılır mı), K4 (çekim önerilmeden önce değerlendirilen koruyucu seçenekler).
Hekimden: çekim kararını belirleyen kriterler (kalan diş dokusu, kırık hattı nerede, kemik desteği, hastanın genel durumu); kök ucu lezyonunda ne zaman bekle-gör, ne zaman kanal, ne zaman çekim; "çekilmeli" denilip kurtarılan ve kurtarılamayan birer gerçek gözlem; hangi durumda kurtarmaya çalışmayı doğru bulmaz.
Fotoğraf: kimliksiz periapikal radyografi örneği (lezyon), kırık diş örneği (onamla), kanal cihazları (apeks bulucu, döner alet, büyütme).
İç link: D2, D3, hizmet sayfaları kanal ve çekim; dentaltourism EN karşılığı yok (EN'de E8 farklı açı).

### D4 — Diş ağrısında ne zaman acilen diş hekimine gitmek gerekir? (drdevrim, TR — ilk makale 4)
Soruları: TR4 (gece ağrı, sabaha kadar beklemeli miyim).
Hekimden: hemen aranmayı gerektiren belirtiler (şişlik, ateş, yutma/nefes güçlüğü, travma, kanama), sabaha kadar bekleyebilecek durumlar, hastaya evde ne yapmasını / yapmamasını söylediği, antibiyotiği kendi başına başlamaya yaklaşımı (klinik görüş), gece gelen gerçek bir vaka gözlemi.
Fotoğraf: klinik dış görünüş akşam saatinde, acil seti/ünit.
İç link: B1 (saatler/acil süreci), drdevrim `acil` ve `haftasonu` sayfaları.
Temizlik: devrimbirikensipahi `/soru-cevap/gece-dis-agrisi/` ve `/soru-cevap/dis-agrisini-ne-keser/` → 301 bu yazıya (§5).

### D2 — Dişim çürük ama ağrımıyor: dolgu mu, kanal mı? (drdevrim, TR)
Soruları: TR1, E4 (derin çürükte siniri almadan dişi kurtarmak mümkün mü).
Hekimden: ağrısız çürükte kararı ne belirler (derinlik, pulpa yakınlığı, soğuk/sıcak testi, radyografi); derin çürükte pulpayı koruma yaklaşımı (hangi durumda, hangi malzeme adı), başarısız olursa ne olur; "ağrımıyorsa bekleyelim" diyen hastaya ne söyler; hastanın fark etmediği ama sık gördüğü bir sorun.
Fotoğraf: kimliksiz bite-wing/periapikal çürük örneği, kullanılan dolgu/kaide materyali.

### D8 — Dişlerimi kestirmeden estetik yaptırabilir miyim? Bonding, lamina, zirkonyum: kime hangisi (drdevrim, TR)
Soruları: TR7, TR8 (zirkonyum mu kompozit bonding mi), ES3 (ayrık ön dişler ortodontisiz kompozitle kapatılır mı), ES4 (kompozit lamina ile porselen lamina gerçek farklar), K5 (bonding/lamina/zirkonyum kararı nasıl verilir).
Hekimden: karar ağacı (renk mi form mu, diş dokusu kaybı, kapanış, diş sıkma, yaş, bütçe değil ihtiyaç); hangi hastaya hangisini önermez; ömür ve bakım konusunda kendi gözlemi (rakam veriyorsa kendi rakamı); mock-up/şablon kullanımı; ayrık dişte kompozitin sınırı.
Fotoğraf: mock-up aşaması, kompozit ve seramik örnekleri, onamlı önce/sonra (abartısız).
Not: dentaltourism EN'de E8/E9 farklı açıyla; birbirine link, kopya değil.

### D5 — İmplant mı, köprü mü? (drdevrim, TR)
Soruları: TR6.
Hekimden: köprüyü hâlâ önerdiği durumlar; implantı önermediği durumlar; komşu dişlerin durumu kararı nasıl etkiler; süre ve seans farkı (kendi pratiği); gerçek bir karar örneği.
Fotoğraf: model üzerinde köprü ve implant, tomografi ekranı.

### ~~E7 — Can I send my dental X-ray for a preliminary assessment?~~ ✅ yayında 20.11.2026 (EN; çeviri yok; yeni soru sorulmadan, E1 cevaplarıyla — docs/yazilar/e7-send-your-dental-x-ray.md; /about/ süreç bölümü henüz güncellenmedi)
Soruları: EN7, K3'ün EN sürümü, K7 (yurt dışı hastanın ilk başvurudan tedavi sonrasına süreci).
Hekimden: hangi görüntü yeterli (panoramik/tomografi), neyi uzaktan söyleyebilir, neyi söyleyemez; ön değerlendirmede hasta ne alır (yazılı plan? seçenekler?); gelişte planın değiştiği gerçek bir örnek; tipik program (1. gün muayene/tomografi … son gün kontrol); hangi ülkelerden en çok hasta ve en sık hangi tedaviler.
Fotoğraf: WhatsApp'ta görüntü alma akışının kimliksiz ekranı, plan anlatım anı, tomografi ekranı.
Bağlantılar: /packages/, /about/, /treatments/dental-implants/; drdevrim EN/DE/RU/BG pSEO sayfalarından bu yazıya blok.

### E4 — Dental implants in Turkey: how many visits do you really need? (dentaltourism, EN → çeviriler — ilk makale 3)
Soruları: EN4 (tek seyahatte implant tamamlanır mı), ilk makale 3.
Hekimden: aşamalar ve bekleme süreleri (kendi protokolü), tek seyahatte bitenler/bitmeyenler, aynı gün yükleme hangi durumda, iki gelişin planı, ülkesine dönünce kontrolü nasıl yaptığı.
Fotoğraf: zaman çizelgesi grafiği (kendi verimizle), geçici protez örneği, implant belgesi.
Bağlantılar: /treatments/dental-implants/, /packages/dental-implants/, E6, E7.

### ~~E1 — Is it safe to get dental implants in Turkey?~~ ✅ yayında 19.11.2026 (EN; hekim kararı: şimdilik çeviri yok)
Soruları: EN1.
Hekimden: güvenliği belirleyen gerçek faktörler (planlama, tomografi, sterilizasyon, hekim deneyimi, malzeme izlenebilirliği), riskleri açıkça; "ucuz ve hızlı" talebine nasıl yanıt verdiği; yurt dışında yapılmış ve sorun çıkan vakalarla karşılaşıyor mu, en sık hata ne.
Fotoğraf: sterilizasyon, implant belgesi, tomografi.
Temizlik: devrimbirikensipahi `/blog/english/is-it-safe-dental-work-turkey/` (2.583 kelime) tohum metin; yeni yazı indekslenince 301.
Bağlantılar: /guide/dental-care-turkey/, /guide/teeth-done-in-turkey/ (rehber gövdeleri de aynı cevaplarla kalınlaştırılır).

### E8 — Why do some dentists refuse to place crowns on healthy teeth? (dentaltourism, EN → çeviriler — ilk makale 2)
Soruları: ilk makale 2, EN11 (sağlam dişleri kestirmeden gülüşümü düzeltebilir miyim).
Hekimden: sağlam dişe kaplamayı reddettiği durumlar ve gerekçesi, hastaya sunduğu alternatif (bonding, beyazlatma, ortodonti yönlendirmesi), geri dönüşsüzlük konusunu nasıl anlattığı, reddettiği gerçek bir talep örneği. (Misafir yazılarda verilen ifadeler kullanılabilir: "Hollywood smile'a hayır dediğim durumlar".)
Fotoğraf: minimal preparasyon örneği (onamlı), kompozit örnekleri.

### E6 — What happens if my dental implant fails after I return home? (dentaltourism, EN → çeviriler; aynı cevaplar /guide/dental-guarantee-aftercare/ gövdesine)
Soruları: EN6, K8 (komplikasyonda destek).
Hekimden: başarısızlık belirtileri, hasta ülkesindeyken ilk adım (fotoğraf/radyografi gönderimi, yerel hekimle iletişim), hangi durumda İstanbul'a dönmesi gerekir, garanti/yenileme politikası yazılı mı ve neyi kapsamaz, gerçekten yaşanmış bir örnek (misafir yazı: "başarısız implant yenilendi").
Fotoğraf: yazılı garanti/implant belgesi örneği, uzaktan takip ekranı.

### D6 — Tek dişim eksik: implant süreci ne kadar sürer? (drdevrim, TR)
Soruları: TR9, İM1 (kemik erimesi olan hastaya implant), İM2 (çekimle aynı gün implant hangi durumlarda yapılmaz), İM6 (implantın üzerine diş neden hemen takılamaz), K6'nın TR hasta sürümü.
Hekimden: tipik süre ve seanslar, aynı gün implantı yapmadığı durumlar, kemik azlığında seçenekler, geçici diş nasıl çözülüyor, bekleme süresini kısaltma talebine yanıt.
Fotoğraf: tomografi kesiti (kimliksiz), implant seti, geçici protez.

### D9 — Sağlam dişe kaplama yapılır mı? Hollywood smile için tüm dişleri kestirmek gerekir mi? (drdevrim, TR)
Soruları: ES1, ES2, ES5 (diş eti çekilmesi olan hastaya estetik kaplama).
Hekimden: sağlam dişe zirkonyumu neden önermediği, kaç dişe karar nasıl verilir, diş eti çekilmesinde estetik kaplamanın sınırı ve önce ne yapılır, reddettiği gerçek talep.
Fotoğraf: onamlı örnek, model üzerinde preparasyon miktarı.

### E9 — What are the risks of getting 20 zirconia crowns in Turkey? (dentaltourism, EN → çeviriler)
Soruları: EN10.
Hekimden: 20 kaplamanın biyolojik bedeli, hangi hastada gerçekten gerekir, alternatifleri, uzun dönemde gördüğü sorunlar, monolitik vs katmanlı zirkonyum tercihi (misafir yazıdaki ifadeler: monolitik çoğu hastaya, e.max daha estetik ama kırılgan, parafonksiyon kontrolü).
Fotoğraf: zirkonyum örnekleri, laboratuvar iş akışı.

### E2 — How do I find a trustworthy dentist in Istanbul? What to ask before choosing (dentaltourism, EN → çeviriler — ilk makale 5)
Soruları: EN2, EN8 (Türk diplomaları uluslararası geçerli mi), ilk makale 5.
Hekimden: hastanın sorması gereken 8–10 soru (kendi listesi), ruhsat/oda kaydı nasıl doğrulanır, diploma ve unvan denkliği hakkında bildiği, plan ve malzemenin yazılı verilmesi, uzun dönem takip sorusu.
Fotoğraf: ruhsat/oda belgesi (kimliksiz), diplomalar.
Bağlantılar: /guide/best-dental-clinic-istanbul/ (rehber ticari kalır, yazıya link), D10 (TR karşılığı).

### D3 — Kanal tedavili dişim tekrar ağrıyor: yeniden kanal mı, çekim mi? Kaplama şart mı? (drdevrim, TR)
Soruları: E2 (daha önce kanal yapılmış diş tekrar ağrıyor, çekim şart mı), E5 (kanal tedavili dişe mutlaka kaplama gerekir mi).
Hekimden: yeniden kanal (retreatment) hangi durumda, hangi durumda çekim; kaplama kararını ne belirler (kalan doku, dişin yeri); tek/iki seans tercihi; gerçek bir örnek.
Fotoğraf: kimliksiz radyografi (eski kanal, lezyon), büyütme/mikroskop varsa.

### E3 — What is actually included in a dental treatment quote in Turkey? (dentaltourism, EN → çeviriler; /prices/ gövdesine özet) — fiyat yok
Soruları: EN3 (full mouth restoration maliyeti — rakamsız: teklif nasıl oluşur), EN9 (teklife hangi işlemler dahildir).
Hekimden: teklifin nasıl hazırlandığı (muayene sonrası yazılı, kalem kalem), neyin dahil olduğu (geçici, kontrol, görüntüleme, laboratuvar), neyin dahil olmadığı, teklifin değişebildiği durumlar, "tüm ağız" talebine yaklaşım. Rakam yok, kur yok.
Fotoğraf: kimliksiz teklif şablonu.

### D7 — Diş eti sağlığı ve implant (drdevrim, TR)
Soruları: İM3 (implant çevresinde kanama peri-implantitis midir), İM4 (implant etrafı diş eti neden çekilir), İM5 (sigara ve implant başarısı), İM7 (diş eti hastalığı tedavi edilmeden implant yapılabilir mi).
Hekimden: implant öncesi periodontal tedavi şartı, sigara içen hastaya söylediği, peri-implantitis belirtileri ve ne yaptığı, diş eti çekilmesinin nedenleri ve önlemi, gerçek bir örnek.
Fotoğraf: periodontal muayene, bakım ürünleri, kontrol seansı.

### E5 — How many days should I stay in Istanbul for crowns and veneers? (dentaltourism, EN → çeviriler)
Soruları: EN5.
Hekimden: kaplama/lamina için seans düzeni ve laboratuvar süresi (kendi pratiği), prova sayısı, kısaltma talebine yanıt, geçici ile ülkesine dönen hasta olur mu.
Fotoğraf: laboratuvar/prova anı, geçici kaplama.

### E10 — What should I do if I need emergency dental care while visiting Istanbul? (dentaltourism, EN → çeviriler)
Soruları: EN12.
Hekimden: turistin acilde ilk yapacağı, kliniğin acil kabul düzeni (B1 ile aynı), dil desteği, sigorta belgesi hazırlanıyor mu, kısa süreli çözüm vs kalıcı tedavi ayrımı.
Fotoğraf: B1 ile ortak.
Bağlantılar: /treatments/emergency-dentistry/, B1.

### D10 — İstanbul'da diş hekimi seçerken nelere dikkat etmeliyim? (drdevrim, TR)
Soruları: TR10.
Hekimden: E2'deki listenin Türk hasta sürümü; yorumları okurken nelere baktığı; "kampanya" ve "paket" diliyle ilgili görüşü; ikinci görüşe yaklaşımı.
Fotoğraf: hekimler, klinik.

## 3. Hekimden toplu istenenler (bir oturumda alınabilir)
Çalışma saatleri ve acil düzeni · tedavi listesi ve yapılmayanlar · eğitim/unvan ayrıntıları (Devrim, Ekin) · cihaz listesi (görüntüleme, sterilizasyon, tarayıcı) · implant markaları, yıl ve yaklaşık sayı · garanti/takip politikası (yazılı?) · en çok hasta gelen ülkeler ve tedaviler · konuşulan diller. Bunlar birden çok parçayı besler; ilk oturumda alınırsa Gün 1–5 ve E-serisi hızlanır.

## 4. Soru → yer (tek tek)

| # | Soru | Parça | Site |
|---|---|---|---|
| TR1 | Dişim çürük ama ağrımıyor. Dolgu mu kanal mı? | D2 | drdevrim |
| TR2 | Dişimi çektirmeden kurtarmak mümkün mü? | D1 | drdevrim |
| TR3 | Şişli'de pazar günü açık diş hekimi var mı? | B1 | devrimbirikensipahi |
| TR4 | Gece dişim ağrıyor, sabaha kadar beklemeli miyim? | D4 | drdevrim |
| TR5 | Kanal tedavisi mi çekim mi? | D1 | drdevrim |
| TR6 | İmplant mı köprü mü? | D5 | drdevrim |
| TR7 | Dişlerimi kestirmeden estetik yaptırabilir miyim? | D8 | drdevrim |
| TR8 | Zirkonyum mu kompozit bonding mi? | D8 | drdevrim |
| TR9 | Tek dişim eksik, ne kadar sürede implant? | D6 | drdevrim |
| TR10 | İstanbul'da diş hekimi seçerken nelere dikkat? | D10 | drdevrim |
| E1 | Kök ucunda iltihap görülen her dişe kanal yapılır mı? | D1 | drdevrim |
| E2 | Kanal yapılmış dişim tekrar ağrıyor, çekim şart mı? | D3 | drdevrim |
| E3 | Dişimin yarısı kırıldı, kurtarılabilir mi? | D1 | drdevrim |
| E4 | Derin çürükte siniri almadan kurtarmak mümkün mü? | D2 | drdevrim |
| E5 | Kanal tedavili dişe mutlaka kaplama gerekir mi? | D3 | drdevrim |
| İM1 | Kemik erimesi olan hastaya implant yapılır mı? | D6 | drdevrim |
| İM2 | Çekimle aynı gün implant hangi durumlarda yapılmaz? | D6 | drdevrim |
| İM3 | İmplant çevresinde kanama peri-implantitis midir? | D7 | drdevrim |
| İM4 | İmplant etrafındaki diş eti neden çekilir? | D7 | drdevrim |
| İM5 | Sigara içen hastada implant başarısı | D7 | drdevrim |
| İM6 | İmplantın üzerine diş neden hemen takılamaz? | D6 | drdevrim |
| İM7 | Diş eti hastalığı tedavi edilmeden implant yapılır mı? | D7 | drdevrim |
| ES1 | Sağlam dişlere zirkonyum doğru mu? | D9 | drdevrim |
| ES2 | Hollywood Smile için bütün dişleri kestirmek gerekir mi? | D9 | drdevrim |
| ES3 | Ayrık ön dişler ortodonti olmadan kompozitle kapatılır mı? | D8 | drdevrim |
| ES4 | Kompozit lamina ile porselen lamina farkları | D8 | drdevrim |
| ES5 | Diş eti çekilmesi olan hastaya estetik kaplama | D9 | drdevrim |
| ~~EN1~~ | ~~Is it safe to get dental implants in Turkey?~~ ✅ 19.11 | E1 | dentaltourism |
| EN2 | How do I find a trustworthy dentist in Istanbul? | E2 | dentaltourism |
| EN3 | How much does a full mouth restoration cost? (rakamsız) | E3 | dentaltourism |
| EN4 | Can I get implants in Turkey in one visit? | E4 | dentaltourism |
| EN5 | How many days should I stay for crowns? | E5 | dentaltourism |
| EN6 | What if my implant fails after I return home? | E6 | dentaltourism |
| ~~EN7~~ | ~~Can I send my X-ray for a preliminary assessment?~~ ✅ 20.11 | E7 | dentaltourism |
| EN8 | Are Turkish dental qualifications recognized internationally? | E2 | dentaltourism |
| EN9 | What is included in a dental treatment quote? | E3 | dentaltourism |
| EN10 | Risks of 20 zirconia crowns | E9 | dentaltourism |
| EN11 | Restore my smile without shaving healthy teeth? | E8 | dentaltourism |
| EN12 | Emergency dental care while visiting Istanbul | E10 | dentaltourism |
| K1 | Hangi tedaviler uygulanıyor, hangileri uygulanmıyor? | B4 | devrimbirikensipahi |
| K2 | Günler, saatler, pazar ve acil süreç | B1 | devrimbirikensipahi |
| K3 | İlk muayene, radyografi, planlama | B2 (TR) · E7 (EN) | devrimbirikensipahi · dentaltourism |
| K4 | Çekim öncesi koruyucu seçenekler | D1 | drdevrim |
| K5 | Bonding / lamina / zirkonyum kararı | D8 | drdevrim |
| K6 | İmplant marka ve sistemleri, greft | B5 (+ dentaltourism tedavi sayfası) · D6 | devrimbirikensipahi · dentaltourism · drdevrim |
| K7 | Yurt dışı hastanın süreci | E7 + /about/ | dentaltourism |
| K8 | Komplikasyonda destek | E6 + /guide/dental-guarantee-aftercare/ | dentaltourism |
| K9 | Hekimlerin eğitimi, deneyimi, yaklaşımı | D11 · E11 | drdevrim · dentaltourism |
| K10 | Sterilizasyon, kayıt, takip | B3 (+ /about/ EN özeti) | devrimbirikensipahi · dentaltourism |
| M1 | Dişi çekmek mi kurtarmak mı? | D1 | drdevrim |
| M2 | Why do some dentists refuse crowns on healthy teeth? | E8 | dentaltourism |
| M3 | Dental implants in Turkey: how many visits? | E4 | dentaltourism |
| M4 | Diş ağrısında ne zaman acil? | D4 | drdevrim |
| M5 | What to ask before choosing a clinic in Istanbul? | E2 | dentaltourism |

## 5. Temizlik ve kullanıcı kararları

- devrimbirikensipahi `/blog/english/*` (4 İngilizce turist yazısı) → ilgili E-parçası indekslenince 301 (E1: is-it-safe; dental-tourism-turkey-istanbul → /guide/dental-tourism/; dentist-istanbul ve nisantasi-dentist → dentaltourism semt sayfaları).
- devrimbirikensipahi `/soru-cevap/gece-dis-agrisi/`, `/soru-cevap/dis-agrisini-ne-keser/` → 301 D4; `/soru-cevap/kanal-tedavisi-ne-zaman-yapilmali/` → 301 D1. Diğer soru-cevap yazıları kalır.
- devrimbirikensipahi `/blog/en-iyi-disci/*` (~55 ince "X açık dişçi" yazısı) ve drdevrim `en-iyi-disci` ailesi (398): "en iyi" üstünlük ifadesi mevzuat riski. Karar: yeniden adlandırma / 301 / noindex.
- GBP (kullanıcı): ad = tabela/ruhsat adı, açıklama ve "|" yok; kategoriler Dentist (birincil), Dental clinic, Cosmetic dentist, gerçekse Emergency dental service; sahip olunmayan uzmanlık kategorileri yok; saatler B1 ile aynı; logo ve kapak = sitelerdeki aynı görsel.
- Ölçüm: GSC servis hesabı; Bing Webmaster Tools doğrulaması (dentaltourism, drdevrim).

## 6. Claude'un ek soruları (AEO: yapay zekâya sorulan, hekim cevabı olmadan doğru yazılamayan)

Danışman listesinin dışında, bir yapay zekâ olarak kendim de cevabını bilmediğim ve hastaların arama motoruna / sohbet
botuna sorduğu sorular. Her biri ya mevcut bir parçaya eklenir ya da yeni kısa yazı olur. Hekim seçer.

| # | Soru (hastanın sorduğu biçim) | Neden YZ cevaplayamıyor | Nereye |
|---|---|---|---|
| ~~C1~~ ✅ | Başka klinikte başarısız olmuş implantımı yeniden yaptırabilir miyim? Ne getirmeliyim? | cevaplandı 19.11 | E1'e bölüm eklendi |
| ~~C2~~ ✅ | Kemik yetersizse ne oluyor: greft / sinüs lift yapıyor musunuz, süre nasıl değişiyor? | cevaplandı 19.11 | E1 SSS |
| ~~C3~~ ✅ | Ülkemdeki diş hekimim takibi / kaplamayı yapabilir mi? Yabancı hekimle nasıl çalışıyorsunuz? | cevaplandı 19.11 | E1 |
| ~~C4~~ ✅ | Diş hekimi korkum var; sedasyon / uyutma var mı? Nasıl yaklaşıyorsunuz? | cevaplandı 19.11 | E1 SSS |
| ~~C5~~ ✖ | İlk randevu nasıl geçer, saat saat? Aynı gün tedaviye başlanır mı? | atlandı (hekim) | — |
| ~~C6~~ ✅ | Neden S.I.N. implant? Premium sistemden farkı sadece fiyat mı? | cevaplandı 19.11 | E1 |
| ~~C7~~ ✖ | All-on-4 / tüm çene için gerçekçi takvim nedir, kaç seyahat? | atlandı (hekim) | — |
| ~~C8~~ ✅ | İstanbul'dayken ameliyattan sonraki gece sorun olursa kime ulaşırım? | cevaplandı 19.11 | E1 |
| ~~C9~~ ✅ | Dt. / Dr. Dt. / Uzm. Dt. ne demek? Türkiye'de kim "implantolog" diyebilir? | cevaplandı 19.11 | E2 bekliyor |
| ~~C10~~ ✅ | Son kaplamaların rengini / şeklini beğenmezsem uçmadan önce değişir mi? Prova var mı? | cevaplandı 19.11 | E5 bekliyor |
| ~~C11~~ ✖ | Türbin ve el aletlerini nasıl sterilize ediyorsunuz; otoklav sınıfı ne, kayıt tutuluyor mu? | atlandı (hekim) | — |
| ~~C12~~ ✅ | Hangi ülkelerden hasta geliyor, en sık hangi tedavi için? | cevaplandı 19.11 | E1 |
| ~~C13~~ ✅ | Önceki hastalarla konuşabilir miyim / referans veriyor musunuz? | cevaplandı 19.11 | E1 SSS |
| ~~C14~~ ✅ | Bruksizm (gece sıkma) varsa implant ve kaplama sonrası gece plağı veriyor musunuz? | cevaplandı 19.11 | D7/E9 bekliyor |
| ~~C15~~ ✅ | Kayıtlarım, fotoğraflarım, radyografim nasıl saklanıyor, paylaşılıyor mu (KVKK/GDPR)? | cevaplandı 19.11 | B3 bekliyor |
| ~~C16~~ ✅ | Hangi dilleri konuşuyorsunuz, tercüman var mı? | cevaplandı 19.11 | E1 SSS + RU notu |
| C17 | İmplant sonrası kaç ayda bir kontrol; kontrolü ülkemde yaptırabilir miyim? | Takip protokolü | E6 |
| C18 | Ödeme nasıl: kapora, taksit, kart / nakit, hangi para birimi? (rakamsız) | Klinik politikası | E3 |

